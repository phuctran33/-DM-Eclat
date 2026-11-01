"""Network-free regression checks for source acquisition and canonical adaptation."""
import csv,hashlib,importlib.util,io,json,subprocess,tempfile,unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("application_source",ROOT/"scripts/prepare_application_data.py")
source=importlib.util.module_from_spec(spec);spec.loader.exec_module(source)

class SourceTests(unittest.TestCase):
    def test_offline_missing_source(self):
        with tempfile.TemporaryDirectory() as temporary,patch.object(source,"ROOT",Path(temporary)):
            with self.assertRaises(FileNotFoundError):source.prepare("groceries",offline=True)

    def test_bad_checksum_preserves_existing_canonical(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);cache=root/".tools/downloads";cache.mkdir(parents=True)
            (cache/"groceries-source.csv").write_bytes(b"corrupt cached source")
            output=root/"data/applications";output.mkdir(parents=True);(output/"groceries.csv").write_bytes(b"keep canonical")
            with patch.object(source,"ROOT",root):
                with self.assertRaisesRegex(ValueError,"checksum"):source.prepare("groceries",offline=True)
            self.assertEqual((output/"groceries.csv").read_bytes(),b"keep canonical")

    def test_canonical_adapter_preserves_baskets_and_other_manifest_rows(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);cache=root/".tools/downloads";cache.mkdir(parents=True)
            raw=cache/"groceries-source.csv"
            # Synthetic adapter fixture matching the documented source dimensions.
            rows=[[f"item-{i%169}"] for i in range(9835)];rows[0].append(rows[0][0])
            with raw.open("w",encoding="utf-8",newline="") as stream:csv.writer(stream,lineterminator="\n").writerows(rows)
            data=root/"data";data.mkdir();manifest=data/"manifest.csv"
            fields=["dataset","module","owner","original_source","public_snapshot_url","revision","license","sha256","local_path","status"]
            sentinel={k:"" for k in fields};sentinel.update(dataset="retail",owner="A",status="pending")
            grocery={k:"" for k in fields};grocery.update(dataset="groceries",owner="B",status="pending")
            with manifest.open("w",encoding="utf-8",newline="") as stream:
                writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader();writer.writerows([sentinel,grocery])
            checksum=hashlib.sha256(raw.read_bytes()).hexdigest()
            with patch.object(source,"ROOT",root),patch.object(source,"GROC_HASH",checksum),redirect_stdout(io.StringIO()):source.prepare("groceries",offline=True)
            with (data/"applications/groceries.csv").open(encoding="utf-8",newline="") as stream:canonical=list(csv.DictReader(stream))
            self.assertEqual(len(canonical),9836)
            self.assertEqual(len({row["basket_id"] for row in canonical}),9835)
            self.assertEqual(canonical[0],canonical[1]) # adapter preserves duplicate raw products for Julia audit
            with manifest.open(encoding="utf-8",newline="") as stream:updated=list(csv.DictReader(stream))
            self.assertEqual(updated[0],sentinel)
            self.assertEqual(updated[1]["status"],"verified_source")

    def test_failed_download_never_promotes_partial_file(self):
        with tempfile.TemporaryDirectory() as temporary:
            target=Path(temporary)/"source.csv"
            def fail(command,**kwargs):
                Path(command[-1]).write_bytes(b"partial")
                raise subprocess.CalledProcessError(1,command)
            with patch.object(source.shutil,"which",return_value="curl"),patch.object(source.subprocess,"run",side_effect=fail):
                with self.assertRaises(subprocess.CalledProcessError):source.fetch("https://example.invalid/source",target,False)
            self.assertFalse(target.exists())

if __name__=="__main__":unittest.main(verbosity=2)
