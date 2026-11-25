"""Reproduce the four measured inputs without modifying historical evidence."""
import argparse
import gzip
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import subprocess
import tempfile
import tomllib
from zlib import error as ZlibError

from benchlib import ROOT

MAX_INPUT_BYTES = 16 * 1024 * 1024


def normalize(raw, item_offset):
    compressed = raw.startswith(b"\x1f\x8b")
    if compressed:
        with gzip.GzipFile(fileobj=BytesIO(raw)) as stream:
            data = stream.read(MAX_INPUT_BYTES + 1)
    else:
        data = raw
    if not 0 < len(data) <= MAX_INPUT_BYTES:
        raise ValueError("empty or oversized transaction file")

    rows = []
    for number, line in enumerate(data.decode("ascii").splitlines(), 1):
        tokens = line.split()
        if not tokens or any(not token.isdecimal() for token in tokens):
            raise ValueError(f"line {number}: expected integer item IDs")
        items = [int(token) + item_offset for token in tokens]
        if items[0] <= 0 or any(a >= b for a, b in zip(items, items[1:])):
            raise ValueError(f"line {number}: item IDs must normalize to positive, sorted and unique")
        rows.append(" ".join(map(str, items)))
    return ("\n".join(rows) + "\n").encode("ascii"), compressed


def verify(path, source, expected):
    with path.open("rb") as stream:
        raw = stream.read(MAX_INPUT_BYTES + 1)
    if len(raw) > MAX_INPUT_BYTES:
        raise ValueError("oversized source file")
    normalized, compressed = normalize(raw, source["item_offset"])
    digest = sha256(normalized).hexdigest()
    if digest != expected:
        raise ValueError(f"normalized SHA-256 mismatch: got {digest}, expected {expected}")
    record = dict(source_id=source["id"], source_url=source["url"], raw_sha256=sha256(raw).hexdigest(),
                  raw_bytes=len(raw), gzip=compressed, item_offset=source["item_offset"],
                  normalized_sha256=digest, normalized_bytes=len(normalized))
    return normalized, record


def acquire(dataset, raw_dir, expected, offline):
    name = dataset["name"]
    sources = []
    for source in dataset["sources"]:
        # Keep compatibility with raw FIMI caches created by the original script.
        suffix = "" if source["id"] == "rpi" else "." + source["id"]
        sources.append((source, raw_dir / f"{name}{suffix}.dat"))

    errors = []
    invalid_source = (OSError, EOFError, ValueError, ZlibError)
    for source, cached in sources:
        if cached.is_file():
            try:
                normalized, record = verify(cached, source, expected)
                return normalized, dict(dataset=name, from_cache=True, **record)
            except invalid_source as error:
                errors.append(f"cache {cached.name}: {error}")
    if not offline:
        raw_dir.mkdir(parents=True, exist_ok=True)
        for source, cached in sources:
            try:
                with tempfile.TemporaryDirectory(dir=raw_dir) as staging:
                    download = Path(staging) / "download.part"
                    subprocess.run(["curl", "-fLsS", "--retry", "1", "--retry-max-time", "35",
                                    "--connect-timeout", "8", "--max-time", "25", "--max-filesize",
                                    str(MAX_INPUT_BYTES), source["url"], "-o", str(download)],
                                   check=True, capture_output=True, encoding="utf-8",
                                   errors="replace", timeout=65)
                    normalized, record = verify(download, source, expected)
                    download.replace(cached)
                return normalized, dict(dataset=name, from_cache=False, **record)
            except subprocess.CalledProcessError as error:
                errors.append(f'{source["id"]}: curl exit {error.returncode} {(error.stderr or "").strip()}')
            except subprocess.TimeoutExpired:
                errors.append(f'{source["id"]}: download timed out')
            except invalid_source as error:
                errors.append(f'{source["id"]}: {error}')
    tried = "; ".join(errors) if errors else "no cached source"
    mode = " (offline)" if offline else ""
    raise ValueError(f"No verified benchmark source for {name}{mode}: {tried}")


def prepare(raw_dir, offline=False, report=None):
    config = tomllib.loads((ROOT / "configs/datasets.toml").read_text(encoding="utf-8"))
    historical = json.loads((ROOT / "results/raw/dataset_provenance.json").read_text(encoding="utf-8"))
    expected = {row["name"]: row["normalized_sha256"] for row in historical}
    names = [dataset["name"] for dataset in config["datasets"]]
    if len(names) != len(expected) or set(names) != expected.keys():
        raise ValueError("Acquisition config must cover all measured benchmarks exactly once")
    if report is not None and (report.exists() or report.is_symlink()):
        raise FileExistsError(f"Use a new acquisition report path: {report}")

    # Verify every dataset before replacing any normalized input.
    prepared = [acquire(dataset, raw_dir, expected[dataset["name"]], offline)
                for dataset in config["datasets"]]
    output = ROOT / "data/benchmark"
    output.mkdir(parents=True, exist_ok=True)
    for normalized, record in prepared:
        name = record["dataset"]
        with tempfile.TemporaryDirectory(dir=output) as staging:
            staged = Path(staging) / f"{name}.txt"
            staged.write_bytes(normalized)
            staged.replace(output / staged.name)
        print(json.dumps(record), flush=True)
    if report is not None:
        report.parent.mkdir(parents=True, exist_ok=True)
        with report.open("x", encoding="utf-8", newline="\n") as stream:
            json.dump({"status": "pass", "datasets": [record for _, record in prepared]}, stream, indent=2)
            stream.write("\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=ROOT / ".tools/acquisition")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--report", type=Path, help="New JSON path for this run's source URLs and hashes")
    args = parser.parse_args()
    try:
        prepare(args.raw_dir, args.offline, args.report)
    except (OSError, ValueError) as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
