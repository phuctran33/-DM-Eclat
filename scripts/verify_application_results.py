"""Independently recount application results and compare full maps with Java SPMF."""
import argparse
import csv
import itertools
import json
import subprocess
import tomllib
from fractions import Fraction
from pathlib import Path

from benchlib import CONTRACT, ROOT, compare, minimum_count, read_patterns, sha256, spmf_threshold
from prepare_spmf import JAR_HASH

CLASSES = ("EI", "IE", "N")
APPLICATION_CASES = {
    "groceries": ("groceries",),
    "splice": tuple(f"splice_{label}" for label in CLASSES),
}
APPLICATION_CASES["all"] = APPLICATION_CASES["groceries"] + APPLICATION_CASES["splice"]


def table(path):
    with path.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def counter(path):
    vertical = {}
    with path.open(encoding="utf-8") as stream:
        for tid, row in enumerate(stream):
            for item in map(int, row.split()):
                vertical.setdefault(item, set()).add(tid)

    def count(key):
        return len(set.intersection(*(vertical.get(item, set()) for item in key)))

    return count


def verify_groceries(output, meta, patterns, count):
    n = meta["statistics"]["groceries"]["n_transactions"]
    confidence = Fraction(meta["config"]["groceries"]["minconf"])
    expected = {}
    for union, joint in patterns.items():
        for width in range(1, len(union)):
            for antecedent in itertools.combinations(union, width):
                consequent = tuple(item for item in union if item not in antecedent)
                na, nb = patterns[antecedent], patterns[consequent]
                if Fraction(joint, na) >= confidence:
                    expected[antecedent, consequent] = (joint, na, nb)

    header, rules = table(output / "groceries_rules.csv")
    assert header == CONTRACT["tables"]["groceries_rules"]
    labels = {int(row["item_id"]): row["item_label"] for row in table(output / "prepared/groceries/items.csv")[1]}
    actual, keys = {}, []
    for rank, row in enumerate(rules, 1):
        a = tuple(map(int, row["antecedent_ids"].split()))
        b = tuple(map(int, row["consequent_ids"].split()))
        assert (a, b) not in actual and not set(a) & set(b)
        joint, na, nb = values = tuple(int(row[key]) for key in ("support_count", "antecedent_count", "consequent_count"))
        assert values == expected[a, b] == (count(tuple(sorted(a + b))), count(a), count(b))
        assert int(row["rank"]) == rank and int(row["n_transactions"]) == n
        metrics = joint / n, joint / na, (joint / na) / (nb / n)
        assert all(abs(float(row[key]) - value) < 1e-12
                   for key, value in zip(("support", "confidence", "lift"), metrics))
        assert int(row["length"]) == len(a) + len(b)
        assert row["antecedent_labels"] == " | ".join(labels[item] for item in a)
        assert row["consequent_labels"] == " | ".join(labels[item] for item in b)
        keys.append((-float(row["lift"]), -float(row["confidence"]), -float(row["support"]), len(a) + len(b), a, b))
        actual[a, b] = values
    assert actual == expected and keys == sorted(keys)
    header, top = table(output / "groceries_top10.csv")
    assert header == CONTRACT["tables"]["groceries_rules"] and top == rules[:meta["config"]["groceries"]["top_k"]]
    assert len(rules) == meta["statistics"]["groceries"]["n_rules"]
    print(f"PASS independent Groceries audit: {len(rules)} rules and top {len(top)}")
    return {"n_rules": len(rules), "n_top_rules": len(top)}


def verify_splice(output, meta, maps, counts):
    header, rows = table(output / "dna_patterns.csv")
    assert header == CONTRACT["tables"]["dna_patterns"]
    expected = {key for patterns in maps.values() for key in patterns if 2 <= len(key) <= 4}
    labels = {int(row["item_id"]): row["item_label"] for row in table(output / "prepared/splice/items.csv")[1]}
    actual, keys, infrequent_nonzero = set(), [], 0
    for rank, row in enumerate(rows, 1):
        key = tuple(map(int, row["pattern_ids"].split()))
        assert key not in actual and int(row["rank"]) == rank and int(row["length"]) == len(key)
        actual.add(key)
        assert len({(item - 1) // 4 for item in key}) == len(key)
        assert row["pattern_labels"] == " | ".join(labels[item] for item in key)
        supports = []
        for label in CLASSES:
            name = f"splice_{label}"
            denominator = meta["statistics"]["dna"]["classes"][label]["n_transactions"]
            observed = counts[name](key)
            assert int(row[f"count_{label}"]) == observed and int(row[f"n_{label}"]) == denominator
            support = observed / denominator
            assert abs(float(row[f"support_{label}"]) - support) < 1e-14
            supports.append(support)
            if key not in maps[name] and observed > 0:
                infrequent_nonzero += 1
        span = max(supports) - min(supports)
        assert abs(float(row["support_span"]) - span) < 1e-14
        keys.append((-span, -max(supports), len(key), key))
    assert actual == expected and keys == sorted(keys)
    assert len(rows) == meta["statistics"]["dna"]["n_comparisons"]
    print(f"PASS independent Splice audit: {len(rows)} candidates, {infrequent_nonzero} positive counts below threshold")
    return {"n_dna_candidates": len(rows), "nonzero_infrequent_class_counts": infrequent_nonzero}


def verify(output, java=None, jar=None, *, dataset="all"):
    if not __debug__:
        raise RuntimeError("Application verification requires assertions. Run Python without -O.")
    output = Path(output).resolve()
    meta = tomllib.loads((output / "run.toml").read_text(encoding="utf-8"))
    sources = {"groceries": "groceries", "splice": "dna"}
    selected = sources if dataset == "all" else {dataset: sources[dataset]}
    if set(meta["input_sha256"]) != set(selected) or set(meta["statistics"]) != set(selected.values()):
        raise ValueError(f"Output does not cover the requested application scope: {dataset}")
    for folder, hashes in ((output, meta["artifact_sha256"]), (ROOT, meta["source_sha256"])):
        for path, expected in hashes.items():
            assert sha256(folder / path) == expected, path
    for name, key in selected.items():
        assert sha256(ROOT / meta["config"][key]["input"]) == meta["input_sha256"][name], name

    cases, maps, counts = {}, {}, {}
    for name in APPLICATION_CASES[dataset]:
        if name == "groceries":
            cases[name] = (output / "prepared/groceries/transactions.txt", meta["statistics"][name], "groceries")
        else:
            label = name.removeprefix("splice_")
            cases[name] = (output / f"prepared/splice/transactions_{label}.txt",
                           meta["statistics"]["dna"]["classes"][label], "dna")

    report = {"status": "pass", "cases": {}, "checks": ["artifact/source/input hashes", "all emitted supports"], "spmf": []}
    for name, (path, stats, key) in cases.items():
        own = read_patterns(output / "patterns" / f"{name}.txt")
        with path.open(encoding="utf-8") as stream:
            assert sum(bool(line.strip()) for line in stream) == stats["n_transactions"], name
        assert stats["min_count"] == minimum_count(meta["config"][key]["minsup"], stats["n_transactions"]), name
        count = counter(path)
        assert len(own) == stats["n_patterns"], name
        assert all(value == count(key) and value >= stats["min_count"] for key, value in own.items()), name
        maps[name], counts[name] = own, count
        report["cases"][name] = {key: stats[key] for key in ("n_transactions", "min_count", "n_patterns")}

    if "groceries" in selected:
        report.update(verify_groceries(output, meta, maps["groceries"], counts["groceries"]))
        report["checks"] += ["complete rule splits and metrics", "top-k prefix and ranking"]
    if "splice" in selected:
        dna_maps = {name: maps[name] for name in APPLICATION_CASES["splice"]}
        report.update(verify_splice(output, meta, dna_maps, counts))
        report["checks"].append("complete DNA candidate union and recounted supports")

    if java:
        jar = Path(jar or ROOT / "tools/spmf.jar").resolve()
        assert sha256(jar) == JAR_HASH
        verification = output / "verification"
        verification.mkdir(exist_ok=True)
        java_version = subprocess.run([java, "-version"], capture_output=True, text=True, check=True).stderr.strip()
        for name, (path, stats, key) in cases.items():
            destination = verification / f"{name}.txt"
            threshold = spmf_threshold(meta["config"][key]["minsup"], stats["n_transactions"])
            command = [java, "-jar", str(jar), "run", "Eclat", str(path), str(destination), threshold]
            run = subprocess.run(command, capture_output=True, timeout=180)
            (verification / f"{name}.stdout.log").write_bytes(run.stdout)
            (verification / f"{name}.stderr.log").write_bytes(run.stderr)
            run.check_returncode()
            reference = read_patterns(destination)
            match = compare(maps[name], reference)
            if not match["identical"]:
                raise ValueError(f"{name}: {match}")
            report["spmf"].append(dict(dataset=name, n_patterns=len(reference), exact_match_rate=1.0, identical=True,
                                       jar_sha256=JAR_HASH, java_version=java_version, command=command,
                                       output_sha256=sha256(destination), input_sha256=sha256(path),
                                       threshold_argument=threshold))
            print("SPMF PASS", name, len(reference), flush=True)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dataset", choices=APPLICATION_CASES, default="all")
    parser.add_argument("--java", help="Run pinned live SPMF with this Java >=21 executable")
    parser.add_argument("--jar", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    report = verify(args.output, args.java, args.jar, dataset=args.dataset)
    destination = args.report or args.output / "validation.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Application verification: {destination}")
