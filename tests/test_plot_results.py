"""Export real report tables with a legacy text encoding default."""
import contextlib
import io
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import plot_results
from benchlib import ROOT


class PlotResultsTests(unittest.TestCase):
    def test_report_tables_are_utf8_with_cp1252_default(self):
        # Exercise the real export path, including Vietnamese headers, without
        # changing published results or relying on the host's default encoding.
        real_write_text = Path.write_text
        def legacy_write(path, text, encoding=None, **kwargs):
            return real_write_text(path, text, encoding=encoding or "cp1252", **kwargs)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / "rendered"
            for relative in ["configs/experiments.toml", "results/raw/summary.csv",
                             "results/raw/dataset_statistics.csv", "results/raw/cases.json",
                             "results/correctness/comparisons.csv"]:
                destination = root/relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT/relative, destination)
            (root/"docs/latex").mkdir(parents=True)
            with patch.object(plot_results, "ROOT", root), patch.object(Path, "write_text", legacy_write), \
                    patch("sys.argv", ["plot_results.py", "--results", str(root/"results"),
                                       "--output", str(output), "--report"]), \
                    contextlib.redirect_stdout(io.StringIO()):
                plot_results.main()
            table = root/"docs/latex/generated/benchmark-tables.tex"
            rendered = table.read_bytes()
            self.assertEqual(rendered, (ROOT/"docs/latex/generated"/table.name).read_bytes())
            self.assertEqual(rendered.count(b"\\newcommand"), 8)
            self.assertIn("Mật độ", rendered.decode("utf-8"))
            self.assertIn("Đối chiếu", rendered.decode("utf-8"))
            self.assertEqual(len(list((output/"plots").glob("*.pdf"))), 8)
            self.assertEqual(len(list((output/"plots").glob("*.png"))), 8)
            self.assertFalse((root/"results/plots").exists())
            self.assertFalse((root/"results/raw/optimization.csv").exists())


if __name__ == "__main__":
    unittest.main()
