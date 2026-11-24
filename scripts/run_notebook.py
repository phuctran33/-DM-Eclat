"""Execute one notebook or all three in new Python kernels, then verify the combined results."""
import argparse
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = ("demo", "01_groceries", "02_splice_dna")


def execute(path, output):
    print(f"\nEXECUTE {path.name} in a fresh kernel", flush=True)
    notebook = nbformat.read(path, as_version=4)
    start = time.monotonic()
    client = NotebookClient(notebook, timeout=900, kernel_name="python3")
    try:
        client.execute(cwd=str(ROOT), env={**os.environ, "ECLAT_NOTEBOOK_OUTPUT": str(output)})
    finally:
        nbformat.write(notebook, output.parent / f"{path.stem}-executed.ipynb")
        for cell in notebook.cells:
            if cell.cell_type == "code":
                for entry in cell.get("outputs", []):
                    if entry.output_type == "stream":
                        print(entry.text, end="", flush=True)
    completed = sum(cell.cell_type == "code" and cell.execution_count is not None for cell in notebook.cells)
    print(f"PASS {path.name}: {completed} code cells, {time.monotonic() - start:.1f} s (local/CI)", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--notebook", type=Path, help="Run one notebook instead of the complete suite")
    args = parser.parse_args()
    parent = ROOT / ".tools/notebook-runs"
    parent.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="suite-", dir=parent))
    paths = [args.notebook.resolve()] if args.notebook else [ROOT / "notebooks" / f"{name}.ipynb" for name in NOTEBOOKS]
    for path in paths:
        execute(path, work / path.stem)
    if not args.notebook:
        subprocess.run(
            [sys.executable, "-B", "scripts/verify_delivery.py", "--applications",
             str(work / "01_groceries/applications"), str(work / "02_splice_dna/applications"),
             "--benchmark-review", str(work / "demo/benchmark-review"),
             "--output", str(work / "delivery-validation.json")],
            cwd=ROOT, check=True,
        )
    print(f"Evidence: {work}", flush=True)


if __name__ == "__main__":
    main()
