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
from benchlib import ROOT, CONTRACT, sha256
from benchmark_runner import aggregate

# The original manifest also covers release files now kept in Git history.
ARCHIVED_RELEASE = "556602e66d79f90fa735100e4c58fd0ba59e6d91"


def read(path):
    with open(path, encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def check_manifest(root=ROOT):
    rows = read(root / "results/raw/artifact_sha256.csv")
    if not rows or len({row["path"] for row in rows}) != len(rows):
        raise ValueError("Empty/duplicate benchmark artifact manifest")
    for row in rows:
        name = row["path"].replace("\\", "/")
        archived = (
            name == "docs/Member-A-review.pdf"
            or name.startswith(("docs/latex/figures/", "docs/latex/generated/"))
            or (name.startswith("results/plots/") and name.endswith(".png"))
        )
        if archived:
            data = subprocess.check_output(["git", "show", f"{ARCHIVED_RELEASE}:{name}"], cwd=root)
            size, digest = len(data), hashlib.sha256(data).hexdigest()
        else:
            path = root / name
            size, digest = path.stat().st_size, sha256(path)
        if size != int(row["size_bytes"]) or digest != row["sha256"]:
            raise ValueError(f"Changed measured artifact: {name}")
    return len(rows)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results",type=Path,default=ROOT/"results")
    args=parser.parse_args()
    root=args.results.resolve()
    if root == ROOT / "results":
        print(f"PASS {check_manifest()} frozen artifact hashes (including archived Git paths)")
    rows=read(root/"raw/benchmark_runs.csv")
    comparisons=read(root/"correctness/comparisons.csv")
    assert list(rows[0])==CONTRACT["tables"]["benchmark_runs"]
    assert list(comparisons[0])==CONTRACT["tables"]["comparisons"]
    assert len({r["run_id"] for r in rows})==len(rows),"Duplicate run_id"
    cases=json.loads((root/"raw/cases.json").read_text(encoding="utf-8"))
    protocol=json.loads((root/"raw/protocol.json").read_text(encoding="utf-8"))
    environment=json.loads((root/"raw/environment.json").read_text(encoding="utf-8"))
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
if __name__=="__main__":
    main()
