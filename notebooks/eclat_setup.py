"""Shared environment for the three independent ECLAT notebooks."""
import csv
import hashlib
from importlib.util import find_spec
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

JULIA_VERSION = "1.11.4"
JULIA_SHA256 = "fb3d3c5fccef82158a70677c0044ac5ae40410eceb0604cdc8e643eeff21df8d"


def run(*arguments):
    result = subprocess.run([str(arg) for arg in arguments], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            encoding="utf-8", errors="replace")
    if result.stdout:
        print(result.stdout, end="", flush=True)
    result.check_returncode()
    return result.stdout


def version(executable, flag):
    if not executable:
        return ""
    try:
        return subprocess.check_output([executable, flag], stderr=subprocess.STDOUT, encoding="utf-8")
    except (OSError, subprocess.CalledProcessError):
        return ""


def find_julia(in_colab):
    executable = os.environ.get("ECLAT_JULIA") or shutil.which("julia")
    text = version(executable, "--version")

    def supported(value):
        match = re.search(r"julia version (\d+)\.(\d+)", value)
        return bool(match and tuple(map(int, match.groups())) >= (1, 9))

    if not supported(text) and in_colab:
        cache = Path("/content/.eclat-runtime")
        directory = cache / f"julia-{JULIA_VERSION}"
        executable = directory / "bin/julia"
        if not executable.is_file():
            cache.mkdir(exist_ok=True)
            filename = f"julia-{JULIA_VERSION}-linux-x86_64.tar.gz"
            with tempfile.TemporaryDirectory(dir=cache) as temporary:
                archive = Path(temporary) / filename
                url = f"https://julialang-s3.julialang.org/bin/linux/x64/1.11/{filename}"
                run("curl", "-fLsS", "--retry", "2", "--max-time", "300", url, "-o", archive)
                with archive.open("rb") as stream:
                    actual = hashlib.file_digest(stream, "sha256").hexdigest()
                if actual != JULIA_SHA256:
                    raise ValueError(f"Julia {JULIA_VERSION} archive SHA-256 differs from the official checksum")
                run("tar", "-xzf", archive, "-C", temporary)
                if not executable.is_file():
                    shutil.move(str(Path(temporary) / directory.name), directory)
        executable = str(executable)
        text = version(executable, "--version")
    if not supported(text):
        raise RuntimeError("Need Julia 1.9+. On a local run, put julia on PATH or set ECLAT_JULIA.")
    print(text.strip())
    return executable


def find_java(in_colab):
    executable = os.environ.get("ECLAT_JAVA") or shutil.which("java")

    def supported(candidate):
        text = version(candidate, "-version")
        match = re.search(r'(?:openjdk|java) (?:version )?"?(\d+)', text)
        return bool(match and int(match[1]) >= 21)

    if not supported(executable) and in_colab:
        run("apt-get", "-qq", "update")
        run("apt-get", "-qq", "install", "-y", "openjdk-21-jre-headless")
        executable = "/usr/lib/jvm/java-21-openjdk-amd64/bin/java"
    if not supported(executable):
        raise RuntimeError("Need Java 21+ for SPMF. Set ECLAT_JAVA to the executable if necessary.")
    print(version(executable, "-version").strip())
    return executable


def setup(root, in_colab, name):
    if sys.version_info < (3, 11):
        raise RuntimeError("Need Python 3.11+.")
    os.chdir(root)
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    runtime = "google-colab" if in_colab else "local/CI"
    print(f"SOURCE COMMIT: {commit} RUNTIME: {runtime}")
    print(f"Python {sys.version.split()[0]}")
    julia = find_julia(in_colab)
    java = find_java(in_colab)
    os.environ["ECLAT_JULIA"] = julia
    os.environ["ECLAT_JAVA"] = java
    os.environ.setdefault("JULIA_DEPOT_PATH", str(root / ".tools/julia-depot"))
    run_julia("-e", "using Pkg; Pkg.instantiate()")
    run(sys.executable, "-B", "scripts/prepare_spmf.py", "--java", java)
    if find_spec("matplotlib") is None:
        if not in_colab:
            raise RuntimeError("Install the notebook dependencies from requirements-notebook.txt.")
        run(sys.executable, "-m", "pip", "install", "-r", "requirements-plot.txt")
    parent = root / ".tools/notebook-runs"
    parent.mkdir(parents=True, exist_ok=True)
    if target := os.environ.get("ECLAT_NOTEBOOK_OUTPUT"):
        output = Path(target)
        output.mkdir()
    else:
        output = Path(tempfile.mkdtemp(prefix=f"{name}-", dir=parent))
    print(f"OUTPUT: {output}")
    return output, julia, java


def run_julia(*arguments):
    return run(os.environ["ECLAT_JULIA"], "--startup-file=no", "--project=.", *arguments)


def csv_rows(path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def show_table(headers, rows):
    from IPython.display import Markdown, display

    def line(values):
        escaped = [str(value).replace("|", r"\|") for value in values]
        return "| " + " | ".join(escaped) + " |"

    display(Markdown("\n".join([line(headers), line(["---"] * len(headers)), *(line(row) for row in rows)])))
