"""Audit measured artifacts, archived process logs and the frozen measurement source."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import subprocess
import tarfile
from collections import Counter
from benchlib import ROOT, CONTRACT, sha256, write_csv
from benchmark_runner import aggregate


def read(path):
    with open(path) as stream:
        return list(csv.DictReader(stream))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results",type=Path,default=ROOT/"results")
    parser.add_argument("--write-manifest",action="store_true")
    args=parser.parse_args()
    root=args.results.resolve()
    rows=read(root/"raw/benchmark_runs.csv")
    comparisons=read(root/"correctness/comparisons.csv")
    assert list(rows[0])==CONTRACT["tables"]["benchmark_runs"]
    assert list(comparisons[0])==CONTRACT["tables"]["comparisons"]
    assert len({r["run_id"] for r in rows})==len(rows),"Duplicate run_id"
    cases=json.loads((root/"raw/cases.json").read_text())
    protocol=json.loads((root/"raw/protocol.json").read_text())
    environment=json.loads((root/"raw/environment.json").read_text())
    if all(r["status"]=="ok" for r in rows):
        expected=len(cases)*protocol["config"]["repeats"]*5
        assert len(rows)==expected,(len(rows),expected)
        assert len(comparisons)==2*len(cases)
    assert all(r["identical"]=="True" and float(r["exact_match_rate"])==1 for r in comparisons)
    assert all(int(r[k])==0 for r in comparisons for k in ["missing","extra","wrong_support"])
    for case in cases:
        data=[r for r in rows if r["dataset"]==case["dataset"] and r["minsup"]==case["minsup"]]
        assert data,f"Missing case: {case['dataset']}"
        assert all(r["input_sha256"]==case["input_sha256"] for r in data)
        valid=[r for r in data if r["status"]=="ok"]
        if valid:
            assert len({r["n_patterns"] for r in valid})==1,"Pattern count changed between runs"
            assert len({r["min_count"] for r in valid})==1,"Threshold changed between backends"
    summary=read(root/"raw/summary.csv")
    expected_summary=aggregate(rows)
    assert len(summary)==len(expected_summary)
    for actual,expected in zip(summary,expected_summary):
        for key,value in expected.items():
            if isinstance(value,(int,float)):
                assert math.isclose(float(actual[key]),value,rel_tol=1e-12,abs_tol=1e-12),(key,actual[key],value)
            else:
                assert actual[key]==str(value),(key,actual[key],value)
    measured_commit=environment["git_commit"]
    for path,digest in protocol["source_hashes"].items():
        frozen=subprocess.check_output(["git","show",f"{measured_commit}:{path}"],cwd=ROOT)
        assert hashlib.sha256(frozen).hexdigest()==digest,f"Frozen source mismatch: {path}"
    print(f"PASS frozen measurement source: {measured_commit}")
    archive=root/"logs/benchmark-logs.tar.gz"
    with tarfile.open(archive,"r:gz") as logs:
        for row in rows:
            if row["metric_scope"]!="end_to_end" or row["status"]!="ok":continue
            prefix="benchmark/"+row["run_id"]
            measured=json.load(logs.extractfile(prefix+".json"))
            assert measured["status"]==row["status"]
            assert math.isclose(measured["seconds"],float(row["seconds"]),rel_tol=1e-12)
            assert math.isclose(float(measured["peak_rss_mib"]),float(row["peak_rss_mib"]),rel_tol=1e-12)
            verification=json.load(logs.extractfile(prefix+".output.json"))
            assert verification["verified"] is True and len(verification["output_sha256"])==64
    print(f"PASS {len(cases)} cases, {len(rows)} measurements, {len(comparisons)} exact full-map comparisons")
    print("Statuses:",dict(Counter(r["status"] for r in rows)))
    print("PASS shared headers, unique run IDs, thresholds/counts/hashes, aggregates and archived OS logs")
    if args.write_manifest:
        files=[]
        for directory in [root/"raw",root/"correctness",root/"plots",ROOT/"docs/latex/figures",ROOT/"docs/latex/generated"]:
            files.extend(p for p in directory.glob("*") if p.is_file() and p.suffix in {".csv",".json",".pdf",".png",".tex"}
                         and p.name not in {"checkpoint.json","artifact_sha256.csv"})
        files.extend([archive,ROOT/"docs/Member-A-review.pdf"])
        fields=["path","sha256","size_bytes"]
        write_csv(root/"raw/artifact_sha256.csv",
                  [dict(path=str(p.relative_to(ROOT)),sha256=sha256(p),size_bytes=p.stat().st_size) for p in sorted(set(files))],fields)
        print(f"Wrote hashes for {len(set(files))} evidence/render artifacts")


if __name__=="__main__":
    main()
