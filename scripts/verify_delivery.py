"""Final local/Colab gate: current report, frozen benchmarks, fresh application outputs."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
import tomllib
from benchlib import ROOT, sha256, read_patterns
from build_report import report_sources
from review_benchmarks import check_manifest, check_coverage, current_sources, require_equal
from verify_application_results import verify
from application_tables import tables

def check_report(root=ROOT):
    record=json.loads((root/"docs/report-build.json").read_text("utf-8"))
    if record["status"]!="pass" or sha256(root/"docs/Report.pdf")!=record["pdf_sha256"]:
        raise ValueError("Missing/changed final PDF")
    if record["source_sha256"]!=report_sources(root):
        raise ValueError("Report source changed since PDF build; rebuild first")
    if not 10<=record["body_pages"]<=15:
        raise ValueError("Report body outside 10–15 pages")
    return record

def check_benchmark_review(output):
    output=Path(output).resolve()
    report=json.loads((output/"review.json").read_text("utf-8"))
    if report["status"]!="pass" or report["source_sha256"]!=current_sources():
        raise ValueError("Missing/stale benchmark review")
    expected={"chess","mushroom","retail","T10I4D100K"}
    if {r["dataset"] for r in report["live_cases"]}!=expected or len(report["live_cases"])!=4:
        raise ValueError("Four live benchmark datasets required")
    for path,digest in report["artifact_sha256"].items():
        if sha256(output/path)!=digest:raise ValueError(f"Review evidence changed: {path}")
    for case in report["live_cases"]:
        name=case["dataset"]
        if sha256(ROOT/f"data/benchmark/{name}.txt")!=case["input_sha256"]:
            raise ValueError("Benchmark input changed since live comparison")
        reference=read_patterns(output/f"{name}-spmf.txt")
        for backend in ["list","bitset"]:
            require_equal(read_patterns(output/f"{name}-{backend}.txt"),reference,name)
    return report

def check_published_applications(fresh, published=ROOT/"results/applications"):
    """Bind a fresh run to the published tables and patterns used by the report."""
    fresh = Path(fresh)
    published = Path(published)
    computed = tomllib.loads((fresh/"run.toml").read_text(encoding="utf-8"))["artifact_sha256"]
    recorded = tomllib.loads((published/"run.toml").read_text(encoding="utf-8"))["artifact_sha256"]
    if not recorded or computed != recorded:
        raise ValueError("Fresh application artifacts differ from published report evidence")
    for path, digest in recorded.items():
        artifact = published/path
        # Observation rows and numeric transactions are regenerated from pinned inputs.
        generated_rows = path.startswith("prepared/") and (
            artifact.name == "observations.csv" or artifact.name.startswith("transactions"))
        if generated_rows and not artifact.exists():
            continue
        if sha256(artifact) != digest:
            raise ValueError(f"Published application artifact changed: {path}")

def check_application_spmf(applications):
    live = json.loads((applications / "validation.json").read_text("utf-8"))
    cases = live["spmf"]
    expected = {"groceries", "splice_EI", "splice_IE", "splice_N"}
    names = [case["dataset"] for case in cases]
    if live["status"] != "pass" or set(names) != expected or len(names) != len(expected):
        raise ValueError("Expected one live SPMF comparison each for groceries, splice_EI, splice_IE and splice_N")
    for case in cases:
        name = case["dataset"]
        if not case["identical"] or case["exact_match_rate"] != 1.0:
            raise ValueError(f"Application SPMF mismatch: {name}")
        reference = applications / "verification" / f"{name}.txt"
        if sha256(reference) != case["output_sha256"]:
            raise ValueError(f"Application SPMF evidence changed: {name}")
        require_equal(read_patterns(applications / "patterns" / f"{name}.txt"),
                      read_patterns(reference), name)
    return len(cases)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--applications",type=Path,required=True)
    parser.add_argument("--benchmark-review",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    applications=args.applications.resolve()
    if applications==(ROOT/"results/applications").resolve():
        raise ValueError("Final gate requires outputs mined in this run, not shipped application tables")
    for name,text in tables().items():
        if (ROOT/"docs/latex/generated"/name).read_text("utf-8")!=text:
            raise ValueError(f"Report table differs from CSV: {name}")
    pdf=check_report()
    check_manifest()
    check_coverage(json.loads((ROOT/"results/raw/cases.json").read_text("utf-8")))
    benchmarks=check_benchmark_review(args.benchmark_review)
    apps=verify(applications)
    check_published_applications(applications)
    live_application_count = check_application_spmf(applications)
    try:
        import google.colab
        runtime="google-colab"
    except ImportError:
        runtime="local-or-CI"
    record=dict(status="pass",runtime=runtime,report_pdf_sha256=pdf["pdf_sha256"],
                report_body_pages=pdf["body_pages"],n_rules=apps["n_rules"],
                n_dna_candidates=apps["n_dna_candidates"],
                archived_benchmark_comparisons=benchmarks["archived_full_map_comparisons"],
                live_benchmark_datasets=4,live_application_datasets=live_application_count,
                benchmark_review_sha256=sha256(args.benchmark_review/"review.json"),
                application_validation_sha256=sha256(applications/"validation.json"))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n","utf-8")
    print("PASS final delivery:",json.dumps(record,ensure_ascii=False),flush=True)

if __name__=="__main__":main()
