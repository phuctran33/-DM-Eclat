"""End-to-end controller smoke: tiny real grid, exact comparison and safe resume."""
import csv
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
julia = os.environ.get("ECLAT_JULIA", "julia")
with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    config = root / "smoke.toml"
    config.write_text('''seed=42
warmup_runs=1
repeats=1
timeout_seconds=60
backends=["list","bitset","spmf"]
[[datasets]]
name="basic"
path="data/toy/basic.txt"
minsup=["0.4"]
memory_minsup="0.4"
''')
    cmd = [sys.executable, "scripts/benchmark_runner.py", "--julia", julia, "--config", str(config),
           "--phase", "runtime", "--output", str(root/"results")]
    subprocess.run(cmd, cwd=ROOT, check=True)
    raw = root/"results/raw/benchmark_runs.csv"
    with raw.open() as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 5
    assert all(row["status"] == "ok" and int(row["n_patterns"]) == 7 for row in rows)
    with (root/"results/correctness/comparisons.csv").open() as stream:
        comparisons = list(csv.DictReader(stream))
    assert len(comparisons) == 2 and all(row["identical"] == "True" for row in comparisons)
    before = raw.read_bytes()
    subprocess.run(cmd + ["--resume"], cwd=ROOT, check=True)
    assert raw.read_bytes() == before
    checkpoint=root/"results/raw/checkpoint.json"
    altered=json.loads(checkpoint.read_text())
    altered["signature"]["runtime"]["julia_threads"]="999"
    checkpoint.write_text(json.dumps(altered))
    rejected=subprocess.run(cmd+["--resume"],cwd=ROOT,capture_output=True,text=True)
    assert rejected.returncode!=0 and "runtime environment changed" in rejected.stderr
    assert raw.read_bytes()==before
    logs = list((root/"results/logs/benchmark").glob("*.json"))
    assert len(logs) == 11, len(logs) # 8 processes + 3 output-verification records
    for target in [root/"synthetic-a.txt",root/"synthetic-b.txt"]:
        subprocess.run([julia,"--startup-file=no","--project=.","scripts/generate_synthetic.jl",str(target),"10","50","3","42"],cwd=ROOT,check=True)
    assert (root/"synthetic-a.txt").read_bytes()==(root/"synthetic-b.txt").read_bytes()
    synthetic=[list(map(int,line.split())) for line in (root/"synthetic-a.txt").read_text().splitlines()]
    assert len(synthetic)==50 and all(len(row)==3 and row==sorted(set(row)) for row in synthetic)
    subprocess.run([julia,"--startup-file=no","--project=.","scripts/make_subsets.jl","data/toy/basic.txt",str(root/"subsets"),"42"],cwd=ROOT,check=True)
    previous=b""
    for percent,n in [(10,1),(25,1),(50,2),(75,3),(100,5)]:
        data=(root/f"subsets/subset_{percent}.txt").read_bytes()
        assert data.startswith(previous) and len(data.splitlines())==n
        previous=data
    print("PASS: real toy grid (5 measurements), 2 exact maps, log isolation, safe resume")
    print("PASS: deterministic synthetic rows and nested seeded subsets")
    print("PASS: resume refuses changed runtime without overwriting measurements")
