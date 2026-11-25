"""Network-free regression checks for source acquisition and canonical adaptation."""
import csv,hashlib,importlib.util,io,json,subprocess,tempfile,unittest,zipfile
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

    def test_canonical_adapter_preserves_baskets_and_manifest(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);cache=root/".tools/downloads";cache.mkdir(parents=True)
            raw=cache/"groceries-source.csv"
            # Synthetic adapter fixture matching the documented source dimensions.
            rows=[[f"item-{i%169}"] for i in range(9835)];rows[0].append(rows[0][0])
            with raw.open("w",encoding="utf-8",newline="") as stream:csv.writer(stream,lineterminator="\n").writerows(rows)
            data=root/"data";data.mkdir();manifest=data/"manifest.csv"
            historical=b"dataset,status\ngroceries,verified_source\nretail,verified\n"
            manifest.write_bytes(historical)
            checksum=hashlib.sha256(raw.read_bytes()).hexdigest()
            with patch.object(source,"ROOT",root),patch.object(source,"GROC_HASH",checksum),redirect_stdout(io.StringIO()):source.prepare("groceries",offline=True)
            with (data/"applications/groceries.csv").open(encoding="utf-8",newline="") as stream:canonical=list(csv.DictReader(stream))
            self.assertEqual(len(canonical),9836)
            self.assertEqual(len({row["basket_id"] for row in canonical}),9835)
            self.assertEqual(canonical[0],canonical[1]) # adapter preserves duplicate raw products for Julia audit
            self.assertEqual(manifest.read_bytes(),historical)
            provenance=json.loads((data/"applications/groceries_source.json").read_text(encoding="utf-8"))
            self.assertEqual(provenance["source_sha256"],checksum)

    def test_failed_download_never_promotes_partial_file(self):
        with tempfile.TemporaryDirectory() as temporary:
            target=Path(temporary)/"source.csv"
            def fail(command,**kwargs):
                Path(command[-1]).write_bytes(b"partial")
                raise subprocess.CalledProcessError(1,command)
            with patch.object(source.shutil,"which",return_value="curl"),patch.object(source.subprocess,"run",side_effect=fail):
                with self.assertRaises(subprocess.CalledProcessError):source.fetch("https://example.invalid/source",target,False)
            self.assertFalse(target.exists())

    def test_groceries_never_caches_a_successful_html_response(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            def wrong_response(command, **kwargs):
                Path(command[-1]).write_bytes(b"<html>Error</html>")
            with patch.object(source, "ROOT", root), patch.object(source.shutil, "which", return_value="curl"), \
                    patch.object(source.subprocess, "run", side_effect=wrong_response):
                with self.assertRaisesRegex(ValueError, "checksum"):
                    source.prepare("groceries")
            self.assertEqual(list((root / ".tools/downloads").iterdir()), [])

    def test_splice_falls_back_to_uci_and_reuses_verified_archive(self):
        data = b"EI,fixture," + b"A" * 60 + b"\n"
        checksum = hashlib.sha256(data).hexdigest()
        with tempfile.TemporaryDirectory() as directory:
            cache = Path(directory)
            (cache / "splice-source.data").write_bytes(b"bad mirror bytes")

            def download(command, **kwargs):
                self.assertEqual(command[-3], source.SPLICE_ORIGINAL_URL)
                with zipfile.ZipFile(command[-1], "w") as archive:
                    archive.writestr("splice.data", data)

            with patch.object(source, "SPLICE_HASH", checksum), patch.object(source.shutil, "which", return_value="curl"):
                with patch.object(source.subprocess, "run", side_effect=download) as request:
                    self.assertEqual(source.read_splice(cache, False)[:2], (data, source.SPLICE_ORIGINAL_URL))
                    request.assert_called_once()
                with patch.object(source.subprocess, "run") as request:
                    self.assertEqual(source.read_splice(cache, True)[:2], (data, source.SPLICE_ORIGINAL_URL))
                    request.assert_not_called()

    def test_splice_rejects_bad_zip_without_promoting_cache(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            canonical = root / "data/applications/splice.data"
            canonical.parent.mkdir(parents=True)
            canonical.write_bytes(b"keep canonical")

            def download(command, **kwargs):
                if command[-3] == source.SPLICE_URL:
                    raise subprocess.CalledProcessError(22, command)
                with zipfile.ZipFile(command[-1], "w") as archive:
                    archive.writestr("splice.data", b"wrong checksum")

            with patch.object(source, "ROOT", root), patch.object(source.shutil, "which", return_value="curl"):
                with patch.object(source.subprocess, "run", side_effect=download) as request:
                    with self.assertRaisesRegex(ValueError, "checksum"):
                        source.prepare("splice")
                    self.assertEqual(request.call_count, 2)
            self.assertEqual(canonical.read_bytes(), b"keep canonical")
            self.assertEqual(list((root / ".tools/downloads").iterdir()), [])

if __name__=="__main__":unittest.main(verbosity=2)
