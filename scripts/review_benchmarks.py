"""Member B: audit A's frozen evidence and live-check four full benchmark maps.

This is a correctness review, not a new timing/RSS experiment.
"""
from __future__ import annotations
import argparse
import csv
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
import tomllib
from benchlib import ROOT, compare, minimum_count, read_patterns, sha256, spmf_threshold
from prepare_spmf import JAR_HASH

def csv_rows(path):
    with Path(path).open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))

def check_coverage(cases):
    levels={}
    for case in cases:
        if case["experiment"]=="runtime":
            levels.setdefault(case["dataset"],set()).add(case["minsup"])
    if set(levels)!={"chess","mushroom","retail","T10I4D100K"}:
        raise ValueError("Four runtime datasets required")
    if any(not 5<=len(values)<=7 for values in levels.values()):
        raise ValueError("Five to seven distinct supports required for every dataset")
    return {name:len(values) for name,values in levels.items()}

def require_equal(own, reference, label):
    result=compare(own,reference)
    if not result["identical"]:
        raise ValueError(f"{label}: incomplete/different full map: {result}")
    return result

def current_sources():
    paths=["Project.toml","schemas/contracts.toml","scripts/mine.jl",
           "scripts/review_benchmarks.py","scripts/benchlib.py","scripts/prepare_spmf.py"]
    paths += [p.relative_to(ROOT).as_posix() for p in sorted((ROOT/"src").rglob("*.jl"))]
    return {p:sha256(ROOT/p) for p in paths}

def run(command, log, env):
    result=subprocess.run(list(map(str,command)),cwd=ROOT,env=env,capture_output=True,timeout=300)
    log.with_suffix(".stdout.log").write_bytes(result.stdout)
    log.with_suffix(".stderr.log").write_bytes(result.stderr)
    if result.returncode:
        raise RuntimeError(f"Command failed; see {log}: {result.stderr.decode('utf-8',errors='replace')}")
    return list(map(str,command))

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,required=True,help="New/empty review directory")
    parser.add_argument("--julia",default=os.environ.get("ECLAT_JULIA","julia"))
    parser.add_argument("--java",default=os.environ.get("ECLAT_JAVA","java"))
    args=parser.parse_args()
    out=args.output.resolve()
    if out.exists() and any(out.iterdir()):
        raise ValueError("Review output must be new/empty; preserve old evidence")
    out.mkdir(parents=True,exist_ok=True)
    cases=json.loads((ROOT/"results/raw/cases.json").read_text("utf-8"))
    coverage=check_coverage(cases)
    env={**os.environ,"JULIA_NUM_THREADS":"1"}
    frozen=run([sys.executable,"-B","scripts/verify_artifacts.py"],out/"frozen-artifacts",env)
    print((out/"frozen-artifacts.stdout.log").read_text("utf-8"),end="",flush=True)
    jar=ROOT/"tools/spmf.jar"
    if sha256(jar)!=JAR_HASH: raise ValueError("Wrong SPMF JAR")
    config=tomllib.loads((ROOT/"configs/experiments.toml").read_text("utf-8"))
    records=[]
    for dataset in config["datasets"]:
        name=dataset["name"]; support=str(dataset["memory_minsup"]); source=ROOT/dataset["path"]
        archived=next(c for c in cases if c["dataset"]==name and c["minsup"]==support)
        if sha256(source)!=archived["input_sha256"]:
            raise ValueError(f"Input differs from measured case: {name}")
        with source.open(encoding="utf-8") as stream:
            n=sum(bool(line.strip()) for line in stream)
        if n!=archived["n_transactions"]:raise ValueError("Transaction count mismatch")
        commands={}
        for backend in ["list","bitset"]:
            commands[backend]=run([args.julia,"--startup-file=no",f"--project={ROOT}","scripts/mine.jl",
                                  "--input",source,"--output",out/f"{name}-{backend}.txt",
                                  "--minsup",support,"--backend",backend],out/f"{name}-{backend}",env)
        threshold=spmf_threshold(support,n)
        commands["spmf"]=run([args.java,"-jar",jar,"run","Eclat",source,out/f"{name}-spmf.txt",threshold],
                             out/f"{name}-spmf",env)
        reference=read_patterns(out/f"{name}-spmf.txt")
        for backend in ["list","bitset"]:
            require_equal(read_patterns(out/f"{name}-{backend}.txt"),reference,f"{name}/{backend}")
        count=minimum_count(support,n)
        if any(value<count for value in reference.values()):raise ValueError("Below-threshold output")
        record=dict(dataset=name,minsup=support,min_count=count,n_transactions=n,n_patterns=len(reference),
                    input_sha256=sha256(source),spmf_threshold_argument=threshold,
                    identical=True,exact_match_rate=1.0,commands=commands,
                    output_sha256={b:sha256(out/f"{name}-{b}.txt") for b in ["list","bitset","spmf"]})
        records.append(record)
        print(f"PASS live full maps {name}: {len(reference)} patterns; count={count}; list=bitset=SPMF",flush=True)
    measured=json.loads((ROOT/"results/raw/environment.json").read_text("utf-8"))
    report=dict(status="pass",scope="correctness_only_no_timing_or_rss_claims",
                recorded_at=time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
                platform=platform.platform(),source_commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
                source_sha256=current_sources(),measured_commit=measured["git_commit"],
                frozen_artifact_count=len(csv_rows(ROOT/"results/raw/artifact_sha256.csv")),
                archived_cases=len(cases),support_levels=coverage,live_cases=records,
                spmf_jar_sha256=JAR_HASH,
                julia_version=subprocess.check_output([args.julia,"--version"],text=True).strip(),
                java_version=subprocess.run([args.java,"-version"],capture_output=True,text=True,check=True).stderr.strip(),
                artifact_sha256={p.name:sha256(p) for p in sorted(out.iterdir()) if p.is_file()})
    # Derive measured counts rather than treating the expected experiment size as evidence.
    report["archived_measurements"]=len(csv_rows(ROOT/"results/raw/benchmark_runs.csv"))
    report["archived_full_map_comparisons"]=len(csv_rows(ROOT/"results/correctness/comparisons.csv"))
    (out/"review.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n","utf-8")
    print(f"PASS frozen hashes {report['frozen_artifact_count']}; four live datasets; no measurement artifacts overwritten",flush=True)

if __name__=="__main__":main()
