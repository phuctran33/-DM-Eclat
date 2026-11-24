"""Fetch the pinned official SPMF binary and verify its version and SHA-256."""
import argparse
import re
import subprocess
from benchlib import ROOT, sha256, version

URL = "https://www.philippe-fournier-viger.com/spmf/spmf2.64.jar"
JAR_HASH = "c67c2e56bdd2072eadc0e4bc96c8221cec38c9109f99c4b5f10be8eba64ec250"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--java", default="java")
    args = parser.parse_args()
    jar = ROOT / "tools/spmf.jar"
    if not jar.exists():
        jar.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["curl", "-fLsS", "--retry", "2", "--max-time", "180", URL, "-o", str(jar)], check=True)
    if sha256(jar) != JAR_HASH:
        raise ValueError("JAR hash mismatch; preserve existing jar and install the pinned version explicitly")
    java = version([args.java, "-version"]).splitlines()[0]
    spmf = re.search(r"SPMF version ([\w.]+)", version([args.java, "-jar", str(jar), "version"]))[1]
    print(f"SPMF {spmf}; {java}; SHA256={JAR_HASH}")


if __name__ == "__main__":
    main()
