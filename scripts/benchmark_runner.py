"""Reproducible correctness-gated grid; fresh-process timing plus warm Julia timing."""
from __future__ import annotations
import argparse
import csv
import json
import os
from pathlib import Path
import shutil
import statistics
import subprocess
import sys
import tomllib
from benchlib import (ROOT, CONTRACT, NA, compare, environment, json_write, measure,
                      logpath, minimum_count, read_patterns, sha256, spmf_threshold, write_csv)


def cases(config, phase, julia, output):
    result = []
    if phase in ("pilot", "runtime", "all"):
        for dataset in config["datasets"]:
            for support in ([dataset["memory_minsup"]] if phase == "pilot" else dataset["minsup"]):
                result.append(dict(dataset=dataset["name"], path=ROOT / dataset["path"],
                                   minsup=str(support), experiment="runtime", x=str(support)))
    if phase in ("scalability", "all"):
        dataset = next(d for d in config["datasets"] if d["name"] == config["scalability_dataset"])
        directory = output / "subsets"
        subprocess.run([julia, "--startup-file=no", "--project=.", "scripts/make_subsets.jl",
                        dataset["path"], str(directory), str(config["seed"])], cwd=ROOT, check=True)
        fractions = [10, 25, 50, 75, 100]
        if [round(f * 100) for f in config["scalability_fractions"]] != fractions:
            raise ValueError("make_subsets protocol requires 10/25/50/75/100%")
        for percent in fractions:
            result.append(dict(dataset=f"retail_subset_{percent}", path=directory / f"subset_{percent}.txt",
                               minsup=str(config["scalability_minsup"]), experiment="scalability", x=percent))
    if phase in ("length", "all"):
        for width in config["synthetic_lengths"]:
            path = output / f"synthetic/width_{width}.txt"
            subprocess.run([julia, "--startup-file=no", "--project=.", "scripts/generate_synthetic.jl", str(path),
                            str(config["synthetic_items"]), str(config["synthetic_transactions"]),
                            str(width), str(config["seed"])], cwd=ROOT, check=True)
            result.append(dict(dataset=f"synthetic_width_{width}", path=path,
                               minsup=str(config["synthetic_minsup"]), experiment="length", x=width))
    return result


def aggregate(rows):
    groups = {}
    for row in rows:
        key = tuple(str(row[k]) for k in ("dataset", "minsup", "backend", "metric_scope"))
        groups.setdefault(key, []).append(row)
    output = []
    for key, group in groups.items():
        valid = [r for r in group if r["status"] == "ok"]
        seconds = [float(r["seconds"]) for r in valid]
        rss = [float(r["peak_rss_mib"]) for r in valid if str(r["peak_rss_mib"]) != NA]
        output.append(dict(zip(("dataset", "minsup", "backend", "metric_scope"), key)) |
                      dict(n_runs=len(group), n_ok=len(valid), n_timeout=sum(r["status"] == "timeout" for r in group),
                           n_oom=sum(r["status"] == "oom" for r in group), n_error=sum(r["status"] == "error" for r in group),
                           seconds_median=statistics.median(seconds) if seconds else NA,
                           seconds_min=min(seconds) if seconds else NA, seconds_max=max(seconds) if seconds else NA,
                           peak_rss_mib_median=statistics.median(rss) if rss else NA,
                           peak_rss_mib_min=min(rss) if rss else NA, peak_rss_mib_max=max(rss) if rss else NA,
                           n_patterns=valid[0]["n_patterns"] if valid else NA,
                           n_transactions=group[0]["n_transactions"], min_count=group[0]["min_count"]))
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs/experiments.toml")
    parser.add_argument("--output", type=Path, default=ROOT / "results")
    parser.add_argument("--phase", choices=["pilot", "runtime", "scalability", "length", "all"], default="all")
    parser.add_argument("--julia", default=shutil.which("julia"))
    parser.add_argument("--java", default="java")
    parser.add_argument("--jar", type=Path, default=ROOT / "tools/spmf.jar")
    parser.add_argument("--repeats", type=int)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    if not args.julia:
        parser.error("Julia unavailable; pass --julia /path/to/julia")
    output = args.output.resolve()
    config = tomllib.loads(args.config.read_text())
    if args.repeats is not None:
        config["repeats"] = args.repeats
    if config["repeats"] < 1 or config["warmup_runs"] != 1:
        parser.error("Require repeats>=1 and warmup_runs=1 (preflight)")
    if set(config["backends"]) != {"list", "bitset", "spmf"}:
        parser.error("Correctness gate requires list, bitset, spmf")
    output.mkdir(parents=True, exist_ok=True)
    all_cases = cases(config, args.phase, args.julia, output)
    for case in all_cases:
        case["input_sha256"] = sha256(case["path"])
        with open(case["path"]) as stream:
            case["n_transactions"] = sum(bool(line.strip()) and line[0] not in "#%@" for line in stream)
    source_hashes = {str(p.relative_to(ROOT)): sha256(p) for directory in ["src", "scripts"]
                     for p in sorted((ROOT / directory).rglob("*")) if p.suffix in {".jl", ".py"}}
    signature = dict(config=config, phase=args.phase, source_hashes=source_hashes,
                     input_hashes={c["dataset"]: c["input_sha256"] for c in all_cases},
                     jar_sha256=sha256(args.jar))
    checkpoint_path = output / "raw/checkpoint.json"
    rows, comparisons, completed = [], [], []
    if checkpoint_path.exists():
        if not args.resume:
            parser.error(f"Existing results in {output}; use a different --output or --resume")
        checkpoint = json.loads(checkpoint_path.read_text())
        if checkpoint["signature"] != signature:
            parser.error("Resume refused: config, source, dataset or JAR changed")
        rows, comparisons, completed = checkpoint["rows"], checkpoint["comparisons"], checkpoint["completed"]
    env = environment(args.julia, args.java, args.jar)
    if sys.platform == "darwin":
        env["cpu_model"] = subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand_string"], text=True).strip()
        env["ram_bytes"] = int(subprocess.check_output(["sysctl", "-n", "hw.memsize"], text=True))
    json_write(output / "raw/environment.json", env)
    json_write(output / "raw/protocol.json", signature)
    def save():
        write_csv(output / "raw/benchmark_runs.csv", rows, CONTRACT["tables"]["benchmark_runs"])
        write_csv(output / "correctness/comparisons.csv", comparisons, CONTRACT["tables"]["comparisons"])
        summary = aggregate(rows)
        if summary:
            write_csv(output / "raw/summary.csv", summary, summary[0].keys())
        json_write(checkpoint_path, dict(signature=signature, rows=rows, comparisons=comparisons, completed=completed))
    def command(case, backend, destination):
        if backend == "spmf":
            return [args.java, "-Xmx2g", "-jar", str(args.jar), "run", "Eclat", str(case["path"]), str(destination),
                    spmf_threshold(case["minsup"], case["n_transactions"])]
        return [args.julia, "--startup-file=no", "--project=.", "scripts/mine.jl", "--input", str(case["path"]),
                "--output", str(destination), "--minsup", case["minsup"], "--backend", backend]
    for index, case in enumerate(all_cases):
        cell = f"{case['dataset']}_s{case['minsup']}"
        if cell in completed:
            continue
        print(f"[{index+1}/{len(all_cases)}] {cell}: correctness preflight", flush=True)
        pattern_dir = output / "patterns" / cell
        pattern_dir.mkdir(parents=True, exist_ok=True)
        maps, failures, preflight_results = {}, {}, {}
        for backend in config["backends"]:
            destination = pattern_dir / f"preflight_{backend}.txt"
            result = measure(command(case, backend, destination), output / f"logs/benchmark/{cell}_preflight_{backend}",
                             config["timeout_seconds"])
            preflight_results[backend] = result
            if result["status"] == "ok":
                try:
                    maps[backend] = read_patterns(destination)
                except (ValueError, OSError) as error:
                    failures[backend] = "error"
                    print(f"  invalid {backend} output: {error}", flush=True)
            else:
                failures[backend] = result["status"]
        for backend in ["list", "bitset"]:
            if backend in maps and "spmf" in maps:
                comparison = dict(schema_version="1.0.0", run_id=cell, dataset=case["dataset"], minsup=case["minsup"],
                                  own_backend=backend, reference_backend="spmf", **compare(maps[backend], maps["spmf"]))
                comparisons.append(comparison)
                if not comparison["identical"]:
                    save()
                    raise RuntimeError(f"Correctness mismatch: {cell}/{backend}; timing refused")
        def base_row(backend, repetition, scope):
            return dict(schema_version="1.0.0", run_id=f"{cell}_{backend}_{scope}_{repetition}",
                        dataset=case["dataset"], input_sha256=case["input_sha256"], backend=backend,
                        minsup=case["minsup"], min_count=minimum_count(case["minsup"], case["n_transactions"]),
                        repeat=repetition, seed=config["seed"], n_transactions=case["n_transactions"], n_patterns=NA,
                        metric_scope=scope, seconds=NA, allocated_bytes=NA, peak_rss_mib=NA, status="error",
                        julia_version=env["julia_version"].replace("julia version ", ""),
                        java_version=env["java_version"], spmf_version=env["spmf_version"])
        if failures:
            # Only record processes actually attempted. Do not turn one failed
            # preflight into five fictitious measured repetitions.
            for backend, status in failures.items():
                row = base_row(backend, 1, "end_to_end")
                result = preflight_results[backend]
                row.update(run_id=f"{cell}_{backend}_preflight_failed", status=status,
                           seconds=result["seconds"], peak_rss_mib=result["peak_rss_mib"])
                rows.append(row)
            completed.append(cell)
            save()
            print(f"  timing withheld after failed preflight: {failures}", flush=True)
            continue
        for repetition in range(1, config["repeats"] + 1):
            for backend in config["backends"]:
                row = base_row(backend, repetition, "end_to_end")
                if backend in failures:
                    row["status"] = failures[backend]
                else:
                    destination = pattern_dir / f"timed_{backend}.txt"
                    log = output / f"logs/benchmark/{row['run_id']}"
                    result = measure(command(case, backend, destination), log, config["timeout_seconds"])
                    row.update(seconds=result["seconds"], peak_rss_mib=result["peak_rss_mib"], status=result["status"])
                    if result["status"] == "ok":
                        try:
                            measured_map = read_patterns(destination)
                            if measured_map != maps[backend]:
                                raise ValueError("Timed output differs from preflight")
                            row["n_patterns"] = len(measured_map)
                            json_write(logpath(log, ".output.json"), dict(output_sha256=sha256(destination), verified=True))
                        except (OSError, ValueError) as error:
                            row["status"] = "error"
                            json_write(logpath(log, ".output.json"), dict(verified=False, error=str(error)))
                rows.append(row)
        for backend in ["list", "bitset"]:
            if backend in failures:
                continue
            destination = pattern_dir / f"warm_{backend}.txt"
            log = output / f"logs/benchmark/{cell}_warm_{backend}"
            cmd = [args.julia, "--startup-file=no", "--project=.", "scripts/benchmark_worker.jl", "--batch",
                   str(case["path"]), case["minsup"], backend, str(config["repeats"]), str(destination)]
            result = measure(cmd, log, config["timeout_seconds"])
            if result["status"] == "ok":
                with logpath(log, ".stdout").open() as stream:
                    internal = list(csv.DictReader(stream))
                if len(internal) != config["repeats"] or read_patterns(destination) != maps[backend]:
                    raise RuntimeError(f"Invalid internal benchmark: {cell}/{backend}")
                for measured in internal:
                    row = base_row(backend, int(measured["repeat"]), "internal_read_mine")
                    row.update({k: measured[k] for k in ("seconds", "allocated_bytes", "n_patterns", "status")})
                    rows.append(row)
            else:
                row = base_row(backend, 1, "internal_read_mine")
                row.update(run_id=f"{cell}_{backend}_batch_failed", status=result["status"])
                rows.append(row)
        completed.append(cell)
        save()
        print(f"  complete: counts={ {b:len(m) for b,m in maps.items()} }, failures={failures}", flush=True)
    json_write(output / "raw/cases.json", [{**c, "path": str(c["path"])} for c in all_cases])
    print(f"Saved {len(rows)} measurements; {len(comparisons)} full-map comparisons", flush=True)


if __name__ == "__main__":
    main()
