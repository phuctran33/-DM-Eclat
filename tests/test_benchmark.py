"""Controller checks: real processes, strict maps, count boundaries and aggregation."""
import csv
import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from benchlib import ROOT, compare, json_write, logpath, measure, minimum_count, read_patterns, sha256, spmf_threshold
from benchmark_runner import aggregate, cases, load_checkpoint, main


class ControllerTests(unittest.TestCase):
    @unittest.skipUnless(sys.platform in {"linux", "darwin"}, "Measurement requires Linux/macOS")
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
            processes = []
            real_popen = subprocess.Popen
            def tracked_popen(*args, **kwargs):
                process = real_popen(*args, **kwargs)
                processes.append(process)
                return process
            with patch("benchlib.subprocess.Popen", side_effect=tracked_popen):
                result = measure([sys.executable, "-c", "import time; time.sleep(5)"], Path(tmp)/"timeout", 0.05)
            self.assertEqual(result["status"], "timeout")
            self.assertLess(result["seconds"], 2)
            self.assertIsNotNone(processes[0].poll())
            self.assertEqual(processes[0].returncode, result["exit_code"])
            self.assertEqual(json.loads(logpath(Path(tmp)/"timeout", ".json").read_text(encoding="utf-8"))["status"], "timeout")
            result = measure([sys.executable, "-c", "raise RuntimeError('failure')"], Path(tmp)/"error", 5)
            self.assertEqual(result["status"], "error")

    def test_windows_rejected_before_writing_or_spawning(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)/"results"
            with patch("benchlib.sys.platform", "win32"), patch("benchmark_runner.shutil.which", return_value=None), \
                    patch("benchlib.subprocess.Popen") as popen:
                with self.assertRaisesRegex(ValueError, "Linux/macOS only"):
                    measure([sys.executable, "-c", "pass"], output/"logs/test", 1)
                with patch("sys.argv", ["benchmark_runner.py", "--output", str(output)]), contextlib.redirect_stderr(io.StringIO()) as stderr:
                    with self.assertRaises(SystemExit) as error:
                        main()
                self.assertEqual(error.exception.code, 2)
                self.assertIn("Windows is unsupported", stderr.getvalue())
                popen.assert_not_called()
            self.assertFalse(output.exists())

    def test_existing_artifacts_preserved_before_any_work(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)/"results"
            # Tracked evidence in a fresh checkout has no ignored checkpoint.
            for artifact in ["raw/benchmark_runs.csv", "raw/environment.json", "raw/protocol.json",
                             "plots/existing.pdf", "synthetic/width_5.txt"]:
                path = output/artifact
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(("existing: " + artifact + "\n").encode("utf-8"))
            before = {p.relative_to(output): p.read_bytes() for p in output.rglob("*") if p.is_file()}
            for resume in [[], ["--resume"]]:
                with self.subTest(resume=resume), patch("benchmark_runner.require_measurement_platform"), \
                        patch("benchmark_runner.cases") as generate, patch("benchmark_runner.environment") as env, \
                        patch("benchmark_runner.measure") as run, \
                        patch("sys.argv", ["benchmark_runner.py", "--output", str(output), "--phase", "all"] + resume), \
                        contextlib.redirect_stderr(io.StringIO()) as stderr:
                    with self.assertRaises(SystemExit) as error:
                        main()
                    self.assertEqual(error.exception.code, 2)
                    self.assertIn("No checkpoint" if resume else "different --output", stderr.getvalue())
                    generate.assert_not_called()
                    env.assert_not_called()
                    run.assert_not_called()
                after = {p.relative_to(output): p.read_bytes() for p in output.rglob("*") if p.is_file()}
                self.assertEqual(before, after)

    def test_output_guard_requires_valid_checkpoint(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)/"results"
            self.assertIsNone(load_checkpoint(output, False))
            output.mkdir()
            self.assertIsNone(load_checkpoint(output, False))
            checkpoint = output/"raw/checkpoint.json"
            checkpoint.parent.mkdir()
            for invalid in ["{", "[]", "{}", '{"signature": {}, "rows": null, "comparisons": [], "completed": []}']:
                checkpoint.write_text(invalid, encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "Invalid checkpoint"):
                    load_checkpoint(output, True)
                self.assertEqual(checkpoint.read_text(encoding="utf-8"), invalid)
            valid = dict(signature={}, rows=[], comparisons=[], completed=[])
            json_write(checkpoint, valid)
            self.assertEqual(load_checkpoint(output, True), valid)

    def test_resume_does_not_regenerate_inputs_before_signature_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)/"results"
            config = dict(repeats=1, warmup_runs=1, seed=42, backends=["list", "bitset", "spmf"],
                          synthetic_lengths=[5], synthetic_minsup="0.4")
            config_path = Path(tmp)/"config.toml"
            config_path.write_text('repeats=1\nwarmup_runs=1\nseed=42\nbackends=["list","bitset","spmf"]\n'
                                   'synthetic_lengths=[5]\nsynthetic_minsup="0.4"\n', encoding="utf-8")
            synthetic = output/"synthetic/width_5.txt"
            synthetic.parent.mkdir(parents=True)
            synthetic.write_bytes(b"1 2 3 4 5\n")
            jar = Path(tmp)/"spmf.jar"
            jar.write_bytes(b"test jar: no process should use it")
            json_write(output/"raw/checkpoint.json", dict(signature={}, rows=[], comparisons=[], completed=[]))
            before = {p.relative_to(output): p.read_bytes() for p in output.rglob("*") if p.is_file()}
            with patch("benchmark_runner.subprocess.run") as generate:
                self.assertEqual(cases(config, "length", "unused-julia", output, resume=True)[0]["path"], synthetic)
                with patch("benchmark_runner.require_measurement_platform"), patch("benchmark_runner.environment", return_value={}), \
                        patch("sys.argv", ["benchmark_runner.py", "--output", str(output), "--resume", "--phase", "length",
                                           "--config", str(config_path), "--jar", str(jar), "--julia", "unused-julia"]), \
                        contextlib.redirect_stderr(io.StringIO()) as stderr:
                    # sysctl is a read-only environment query on macOS, so mock
                    # it separately rather than allowing any subprocess.run.
                    with patch("benchmark_runner.subprocess.check_output", return_value="1"):
                        with self.assertRaises(SystemExit) as error:
                            main()
                self.assertEqual(error.exception.code, 2)
                self.assertIn("runtime environment changed", stderr.getvalue())
                generate.assert_not_called()
            self.assertEqual(before, {p.relative_to(output): p.read_bytes() for p in output.rglob("*") if p.is_file()})

    def test_json_unicode_is_utf8_with_legacy_default(self):
        real_write_text = Path.write_text
        def legacy_write(path, data, encoding=None, **kwargs):
            return real_write_text(path, data, encoding=encoding or "cp1252", **kwargs)
        with tempfile.TemporaryDirectory() as tmp, patch.object(Path, "write_text", legacy_write):
            path = Path(tmp)/"metadata.json"
            data = {"dataset": "Mật độ", "machine": "Máy tính"}
            json_write(path, data)
            self.assertEqual(json.loads(path.read_bytes().decode("utf-8")), data)

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
