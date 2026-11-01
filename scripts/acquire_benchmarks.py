"""Acquire, verify, explicitly normalize and describe the four FIMI datasets."""
import argparse
import csv
import gzip
from pathlib import Path
import subprocess
import tomllib
from benchlib import ROOT, json_write, sha256, write_csv


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=ROOT / ".tools/acquisition")
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()
    config = tomllib.loads((ROOT / "configs/datasets.toml").read_text(encoding="utf-8"))
    manifest_path = ROOT / "data/manifest.csv"
    with manifest_path.open(encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames
        # Preserve B's provenance rows exactly.
        manifest = [row for row in reader if row["owner"] != "A"]
    stats = []
    provenance = []
    args.raw_dir.mkdir(parents=True, exist_ok=True)
    for dataset in config["datasets"]:
        name = dataset["name"]
        raw_path = args.raw_dir / f"{name}.dat"
        if not raw_path.exists():
            if args.offline:
                raise FileNotFoundError(raw_path)
            subprocess.run(["curl", "-fLsS", "--retry", "2", "--max-time", "180",
                            dataset["url"], "-o", str(raw_path)], check=True)
        if sha256(raw_path) != dataset["raw_sha256"]:
            raise ValueError(f"Source checksum mismatch: {raw_path}; refusing changed snapshot")
        raw = raw_path.read_bytes()
        data = gzip.decompress(raw) if raw[:2] == b"\x1f\x8b" else raw
        rows = [list(map(int, line.split())) for line in data.decode("utf-8").splitlines() if line.strip()]
        offset = dataset["item_offset"]
        normalized = [[item + offset for item in row] for row in rows]
        if not all(row and min(row) > 0 and row == sorted(set(row)) for row in normalized):
            raise ValueError(f"Unexpected malformed source: {name}")
        output = ROOT / f"data/benchmark/{name}.txt"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text("".join(" ".join(map(str, row)) + "\n" for row in normalized), encoding="utf-8", newline="\n")
        items = set(item for row in normalized for item in row)
        widths = list(map(len, normalized))
        stats.append(dict(dataset=name, n_transactions=len(rows), n_items=len(items),
                          average_width=sum(widths)/len(rows), max_width=max(widths),
                          density=sum(widths)/len(rows)/len(items), input_sha256=sha256(output)))
        manifest.append(dict(dataset=name, module="M3", owner="A", original_source=dataset["url"],
                             public_snapshot_url=dataset["url"], revision="sha256:" + dataset["raw_sha256"],
                             license=dataset["license"], sha256=sha256(output),
                             local_path=str(output.relative_to(ROOT)), status="verified"))
        provenance.append(dict(**dataset, normalized_sha256=sha256(output),
                               transformation=f"gzip decode; add {offset} to every item ID; normalize whitespace; retain all rows",
                               raw_bytes=len(raw), normalized_bytes=output.stat().st_size))
        print(name, stats[-1], flush=True)
    write_csv(manifest_path, manifest, fields)
    write_csv(ROOT / "results/raw/dataset_statistics.csv", stats, stats[0].keys())
    json_write(ROOT / "results/raw/dataset_provenance.json", provenance)


if __name__ == "__main__":
    main()
