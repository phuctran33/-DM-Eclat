"""Regression tests for failures the final-delivery gates must reject."""
import csv
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from benchlib import ROOT,sha256
from review_benchmarks import check_coverage,check_manifest,require_equal
from verify_delivery import check_report

class DeliveryGateTests(unittest.TestCase):
    def test_full_map_rejects_missing_pattern(self):
        with self.assertRaises(ValueError):
            require_equal({(1,):3},{(1,):3,(2,):2},"missing")
    def test_full_map_rejects_wrong_support(self):
        with self.assertRaises(ValueError):
            require_equal({(1,):2},{(1,):3},"support")
    def test_runtime_coverage_requires_every_dataset(self):
        cases=json.loads((ROOT/"results/raw/cases.json").read_text("utf-8"))
        self.assertEqual(set(check_coverage(cases).values()),{6})
        with self.assertRaises(ValueError):
            check_coverage([c for c in cases if c["dataset"]!="retail"])
    def test_runtime_coverage_rejects_missing_levels(self):
        cases=json.loads((ROOT/"results/raw/cases.json").read_text("utf-8"))
        with self.assertRaises(ValueError):
            check_coverage([c for c in cases if c["dataset"]!="chess" or c["minsup"]=="0.85"])
    def test_changed_measured_artifact_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/"results/raw").mkdir(parents=True)
            artifact=root/"evidence.csv";artifact.write_text("original","utf-8")
            with (root/"results/raw/artifact_sha256.csv").open("w",newline="",encoding="utf-8") as stream:
                writer=csv.DictWriter(stream,fieldnames=["path","sha256","size_bytes"]);writer.writeheader()
                writer.writerow(dict(path="evidence.csv",sha256=sha256(artifact),size_bytes=8))
            self.assertEqual(check_manifest(root),1)
            artifact.write_text("tampered","utf-8")
            with self.assertRaises(ValueError):check_manifest(root)
    def test_stale_report_source_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/"docs/latex").mkdir(parents=True)
            (root/"docs/Report.pdf").write_bytes(b"pdf fixture")
            source=root/"docs/latex/Report.tex";source.write_text("original","utf-8")
            record=dict(status="pass",pdf_sha256=sha256(root/"docs/Report.pdf"),body_pages=10,
                        source_sha256={"docs/latex/Report.tex":sha256(source)})
            (root/"docs/report-build.json").write_text(json.dumps(record),"utf-8")
            self.assertEqual(check_report(root)["body_pages"],10)
            source.write_text("new source","utf-8")
            with self.assertRaises(ValueError):check_report(root)

if __name__=="__main__":unittest.main()
