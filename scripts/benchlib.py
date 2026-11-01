"""Shared experiment I/O and process measurement (Python 3.11+, stdlib only)."""
from __future__ import annotations

import csv
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import signal
import subprocess
import sys
import time
import tomllib
from decimal import Decimal
from fractions import Fraction

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = tomllib.loads((ROOT / "schemas/contracts.toml").read_text(encoding="utf-8"))
NA = "NA"


def logpath(prefix, suffix):
    # A decimal minsup in a run ID is not a filename extension.
    return Path(str(prefix) + suffix)


def sha256(path):
    with open(path, "rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def relative(text):
    text = str(text).strip()
    value = Fraction(text[:-1]) / 100 if text.endswith("%") else Fraction(text)
    if not 0 < value <= 1:
        raise ValueError("Relative support must be in (0,1]")
    return value


def minimum_count(text, n):
    value = relative(text) * n
    return max(1, -(-value.numerator // value.denominator))


def spmf_threshold(text, n):
    # SPMF converts a double to ceil(theta*n). Send a fraction strictly inside
    # the SAME absolute-count bin, avoiding floating-point boundary drift.
    count = minimum_count(text, n)
    return str(Decimal(2 * count - 1) / Decimal(2 * n))


def read_patterns(path):
    patterns = {}
    with open(path, encoding="utf-8") as stream:
        for number, raw in enumerate(stream, 1):
            line = raw.strip()
            if not line or line[0] in "#%@":
                continue
            parts = line.split("#SUP:")
            if len(parts) != 2:
                raise ValueError(f"{path}:{number}: invalid pattern")
            items = tuple(sorted(map(int, parts[0].split())))
            support = int(parts[1].strip())
            if not items or len(set(items)) != len(items) or min(items) <= 0 or support <= 0:
                raise ValueError(f"{path}:{number}: invalid items/support")
            if items in patterns:
                raise ValueError(f"{path}:{number}: duplicate itemset {items}")
            patterns[items] = support
    return patterns


def compare(own, reference):
    shared = own.keys() & reference.keys()
    matches = sum(own[k] == reference[k] for k in shared)
    denominator = len(own.keys() | reference.keys())
    return dict(own_count=len(own), reference_count=len(reference), exact_matches=matches,
                missing=len(reference.keys() - own.keys()), extra=len(own.keys() - reference.keys()),
                wrong_support=len(shared) - matches,
                exact_match_rate=matches / denominator if denominator else 1.0,
                identical=own == reference)


def write_csv(path, rows, fields):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def json_write(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def require_measurement_platform():
    """Measurement needs POSIX process groups; reject other OSes before writing."""
    if sys.platform not in {"linux", "darwin"}:
        raise ValueError("Benchmark measurement supports Linux/macOS only; "
                         "Windows is unsupported. Run the controller on Linux or macOS.")


def measure(command, log_prefix, timeout, cwd=ROOT):
    """Wall time and OS peak RSS of a fresh process, including startup and I/O.

    BSD/GNU time measure the complete child lifetime. A timeout kills the whole
    process group. SIGKILL alone is not called OOM without supporting evidence.
    """
    require_measurement_platform()
    prefix = Path(log_prefix)
    prefix.parent.mkdir(parents=True, exist_ok=True)
    monitor = (["/usr/bin/time", "-l"] if platform.system() == "Darwin" else
               ["/usr/bin/time", "-v"] if platform.system() == "Linux" else [])
    if monitor and not Path(monitor[0]).exists():
        monitor = []
    started = time.perf_counter()
    timed_out = False
    with logpath(prefix, ".stdout").open("wb") as out, logpath(prefix, ".stderr").open("wb") as err:
        process = subprocess.Popen(monitor + list(map(str, command)), cwd=cwd,
                                   stdout=out, stderr=err, start_new_session=True)
        try:
            process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass  # The process group may have exited just as the timer fired.
            finally:
                process.wait()
    seconds = time.perf_counter() - started
    stderr = logpath(prefix, ".stderr").read_text(encoding="utf-8", errors="replace")
    peak = NA
    mac = re.search(r"(\d+)\s+maximum resident set size", stderr)
    linux = re.search(r"Maximum resident set size \(kbytes\):\s*(\d+)", stderr)
    if mac:
        peak = int(mac[1]) / 2**20
    elif linux:
        peak = int(linux[1]) / 1024
    status = "timeout" if timed_out else "ok" if process.returncode == 0 else "error"
    if status == "error" and re.search(r"OutOfMemoryError|OutOfMemoryError\(\)|out of memory|Cannot allocate memory", stderr, re.I):
        status = "oom"
    result = dict(command=list(map(str, command)), monitor=monitor, seconds=seconds,
                  peak_rss_mib=peak, exit_code=process.returncode, status=status,
                  timeout_seconds=timeout)
    json_write(logpath(prefix, ".json"), result)
    return result


def version(command):
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=30)
    result.check_returncode()
    return (result.stdout + result.stderr).strip()


def environment(julia, java, jar):
    spmf = version([java, "-jar", str(jar), "version"])
    match = re.search(r"SPMF version ([\w.]+)", spmf)
    return dict(platform=platform.platform(), machine=platform.machine(), processor=platform.processor(),
                cpu_count=os.cpu_count(), julia_version=version([julia, "--version"]),
                java_version=version([java, "-version"]).splitlines()[0],
                spmf_version=match[1] if match else spmf, spmf_jar_sha256=sha256(jar),
                python_version=platform.python_version(), julia_threads=os.getenv("JULIA_NUM_THREADS", "1"),
                git_commit=version(["git", "rev-parse", "HEAD"]),
                git_status=version(["git", "status", "--short"]),
                recorded_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
