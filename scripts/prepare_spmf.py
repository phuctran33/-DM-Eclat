"""Fetch pinned official SPMF binary and optionally regenerate genuine toy references."""
import argparse
import re
import subprocess
from benchlib import ROOT, CONTRACT, json_write, measure, sha256, version, write_csv

URL = "https://www.philippe-fournier-viger.com/spmf/spmf2.64.jar"
JAR_HASH = "c67c2e56bdd2072eadc0e4bc96c8221cec38c9109f99c4b5f10be8eba64ec250"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--references", action="store_true")
    parser.add_argument("--java", default="java")
    args = parser.parse_args()
    jar = ROOT / "tools/spmf.jar"
    if not jar.exists():
        subprocess.run(["curl", "-fLsS", "--retry", "2", "--max-time", "180", URL, "-o", str(jar)], check=True)
    if sha256(jar) != JAR_HASH:
        raise ValueError("JAR hash mismatch; preserve existing jar and install the pinned version explicitly")
    java = version([args.java, "-version"]).splitlines()[0]
    spmf = re.search(r"SPMF version ([\w.]+)", version([args.java, "-jar", str(jar), "version"]))[1]
    print(f"SPMF {spmf}; {java}; SHA256={JAR_HASH}")
    if not args.references:
        return
    rows = []
    for name in ["basic", "dense", "sparse", "duplicates", "boundary"]:
        source = ROOT / f"data/toy/{name}.txt"
        destination = ROOT / f"tests/reference/spmf/{name}.txt"
        command = [args.java, "-jar", "tools/spmf.jar", "run", "Eclat",
                   str(source.relative_to(ROOT)), str(destination.relative_to(ROOT)), "40%"]
        result = measure(command, ROOT / f"results/reference/{name}", 30)
        if result["status"] != "ok":
            raise RuntimeError(f"SPMF reference failed: {name}")
        n = sum(bool(line.strip()) and line[0] not in "#%@" for line in source.read_text(encoding="utf-8").splitlines())
        rows.append(dict(schema_version="1.0.0", dataset=name, input_path=str(source.relative_to(ROOT)),
                         input_sha256=sha256(source), minsup="0.4", min_count=(2*n+4)//5, n_transactions=n,
                         output_path=str(destination.relative_to(ROOT)), output_sha256=sha256(destination),
                         spmf_version=spmf, spmf_jar_sha256=JAR_HASH, java_version=java,
                         command=" ".join(command), status="ok"))
    write_csv(ROOT / "tests/reference/spmf/manifest.csv", rows, CONTRACT["tables"]["spmf_manifest"])
    json_write(ROOT / "results/reference/source.json", dict(url=URL, sha256=JAR_HASH, version=spmf))


if __name__ == "__main__":
    main()
