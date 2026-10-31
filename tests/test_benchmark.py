"""Controller checks: real processes, strict maps, count boundaries and aggregation."""
import csv
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from benchlib import ROOT, compare, logpath, measure, minimum_count, read_patterns, sha256, spmf_threshold
from benchmark_runner import aggregate


class ControllerTests(unittest.TestCase):
    def test_measure_and_timeout(self):
        with tempfile.TemporaryDirectory() as tmp:
            for suffix in ["case_0.4_list", "case_0.4_bitset"]:
                prefix = Path(tmp) / suffix
                result = measure([sys.executable, "-c", "print('real output')"], prefix, 5)
                self.assertEqual(result["status"], "ok")
                self.assertGreater(result["seconds"], 0)
                self.assertIn("real output", logpath(prefix, ".stdout").read_text())
                if sys.platform in {"linux", "darwin"}:
                    self.assertGreater(result["peak_rss_mib"], 0)
            self.assertEqual(len(list(Path(tmp).glob("*.stdout"))), 2)
            result = measure([sys.executable, "-c", "import time; time.sleep(5)"], Path(tmp)/"timeout", 0.05)
            self.assertEqual(result["status"], "timeout")
            self.assertLess(result["seconds"], 2)
            result = measure([sys.executable, "-c", "raise RuntimeError('failure')"], Path(tmp)/"error", 5)
            self.assertEqual(result["status"], "error")

    def test_patterns_and_comparison(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/"patterns.txt"
            path.write_text("3 1 #SUP: 2\n2 #SUP: 4\n")
            self.assertEqual(read_patterns(path), {(1, 3): 2, (2,): 4})
            for text in ["1 #SUP: 2\n1 #SUP: 3\n", "1 1 #SUP: 2\n", "0 #SUP: 1\n", "1 #SUP: 0\n"]:
                path.write_text(text)
                with self.assertRaises(ValueError):
                    read_patterns(path)
        result = compare({(1,): 3, (3,): 1}, {(1,): 2, (2,): 1})
        self.assertEqual([result[k] for k in ["missing", "extra", "wrong_support"]], [1, 1, 1])
        self.assertFalse(result["identical"])
        self.assertEqual(compare({}, {})["exact_match_rate"], 1)

    def test_spmf_count_bins(self):
        for n in [1, 5, 100, 3196, 8124, 88162, 100000]:
            for relative in ["0.07", "0.4", "0.005", "1", "33.3%"]:
                import math
                self.assertEqual(math.ceil(float(spmf_threshold(relative, n))*n), minimum_count(relative, n))

    def test_reference_hashes(self):
        with (ROOT/"tests/reference/spmf/manifest.csv").open() as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(len(rows), 5)
        for row in rows:
            self.assertEqual(sha256(ROOT/row["input_path"]), row["input_sha256"])
            self.assertEqual(sha256(ROOT/row["output_path"]), row["output_sha256"])
            self.assertEqual(row["status"], "ok")

    def test_aggregation_retains_failure(self):
        base = dict(dataset="toy", minsup="0.4", backend="list", metric_scope="end_to_end",
                    peak_rss_mib=100, n_patterns=7, n_transactions=5, min_count=2)
        result = aggregate([dict(base, seconds=1, status="ok"), dict(base, seconds=3, status="ok"),
                            dict(base, seconds=120, status="timeout")])[0]
        self.assertEqual(result["n_runs"], 3)
        self.assertEqual(result["n_timeout"], 1)
        self.assertEqual(result["seconds_median"], 2)


if __name__ == "__main__":
    unittest.main()
