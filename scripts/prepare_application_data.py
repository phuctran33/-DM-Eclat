"""Fetch source data and adapt it to B's frozen inputs; no FIM library is used."""
import argparse,csv,hashlib,json,os,shutil,subprocess,tempfile,zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
GROC_REVISION="d20658ec6d336af2d4ddb5fd72b6f677dd46136e"
GROC_URL=f"https://raw.githubusercontent.com/stedy/Machine-Learning-with-R-datasets/{GROC_REVISION}/groceries.csv"
GROC_HASH="ff1be892fd6b9b57d1a7bc50de067798963dda607619645988b21789bf23ae3b"
SPLICE_ORIGINAL_URL="https://archive.ics.uci.edu/static/public/69/molecular+biology+splice+junction+gene+sequences.zip"
SPLICE_URL="https://www.inf.u-szeged.hu/~tothl/gepitan/uci%20repository/molecular-biology/splice-junction-gene-sequences/splice.data"
SPLICE_HASH="ebbae10c85d3c285e2a2489a37e42bc2ee8d91d15005e391a9962fa3389a114f"

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def fetch(url, path, offline, *, read_verified=None):
    if path.exists():
        return read_verified(path) if read_verified else None
    if offline:
        raise FileNotFoundError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    curl = shutil.which("curl.exe" if os.name == "nt" else "curl")
    if not curl:
        raise RuntimeError("curl is required for acquisition")
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + ".", suffix=".part", delete=False) as stream:
        temporary = Path(stream.name)
    try:
        subprocess.run([curl, "-fLsS", "--retry", "1", "--connect-timeout", "15", "--max-time", "90",
                        url, "-o", str(temporary)], check=True)
        data = read_verified(temporary) if read_verified else None
        os.replace(temporary, path)
        return data
    finally:
        temporary.unlink(missing_ok=True)


def read_splice_archive(path):
    with zipfile.ZipFile(path) as archive:
        return archive.read("splice.data")


def read_splice(cache, offline):
    sources = [
        (cache / "splice-source.data", SPLICE_URL, Path.read_bytes, "University of Szeged academic UCI mirror"),
        (cache / "splice-uci.zip", SPLICE_ORIGINAL_URL, read_splice_archive, "UCI official ZIP, splice.data member"),
    ]
    # Prefer a local copy before attempting a network download.
    errors = []
    for path, url, read, kind in sorted(sources, key=lambda source: not source[0].is_file()):
        def read_verified(candidate):
            data = read(candidate)
            if hashlib.sha256(data).hexdigest() != SPLICE_HASH:
                raise ValueError("Splice pinned source checksum mismatch")
            return data

        try:
            return fetch(url, path, offline, read_verified=read_verified), url, kind
        except (FileNotFoundError, subprocess.CalledProcessError, ValueError, zipfile.BadZipFile, KeyError) as error:
            errors.append(f"{kind}: {error}")
    raise ValueError("No verified Splice source available. " + " | ".join(errors))

def prepare(dataset,offline=False):
    cache=ROOT/".tools/downloads"; destination=ROOT/"data/applications"
    destination.mkdir(parents=True,exist_ok=True)
    if dataset=="groceries":
        source=cache/"groceries-source.csv"
        fetch(GROC_URL,source,offline)
        if digest(source)!=GROC_HASH: raise ValueError("Groceries pinned source checksum mismatch")
        with source.open(encoding="utf-8",newline="") as stream:
            baskets=list(csv.reader(stream,strict=True))
        if len(baskets)!=9835 or len({item for row in baskets for item in row})!=169:
            raise ValueError("Unexpected Groceries source shape")
        output=destination/"groceries.csv"
        with output.open("w",encoding="utf-8",newline="") as stream:
            writer=csv.writer(stream,lineterminator="\n")
            writer.writerow(["basket_id","item_name"])
            for i,basket in enumerate(baskets,1):
                for item in basket:
                    if not item.strip(): raise ValueError(f"Empty product in source basket {i}")
                    writer.writerow([f"groceries:{i:06d}",item])
        provenance=dict(dataset=dataset,source_url=GROC_URL,source_revision=GROC_REVISION,
                        source_sha256=GROC_HASH,adapter="one source CSV row = one basket; long CSV, preserve every item",
                        n_source_baskets=len(baskets),output_sha256=digest(output))
    else:
        data, source_url, source_kind = read_splice(cache, offline)
        rows=list(csv.reader(data.decode("utf-8").splitlines(),strict=True))
        if len(rows)!=3190 or any(len(row)!=3 for row in rows):
            raise ValueError("Unexpected Splice source shape")
        output=destination/"splice.data"; output.write_bytes(data)
        provenance=dict(dataset=dataset,source_url=source_url,source_revision="sha256:"+SPLICE_HASH,
                        original_source="https://doi.org/10.24432/C5M888",original_download_url=SPLICE_ORIGINAL_URL,
                        source_kind=source_kind,source_sha256=SPLICE_HASH,
                        adapter="copy raw records without modification",
                        n_source_records=len(rows),output_sha256=digest(output))
    (destination/f"{dataset}_source.json").write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    manifest=ROOT/"data/manifest.csv"
    with manifest.open(encoding="utf-8",newline="") as stream:
        reader=csv.DictReader(stream); fields=reader.fieldnames; rows=list(reader)
    for row in rows:
        if row["dataset"]==dataset:
            row.update(original_source=GROC_URL if dataset=="groceries" else "https://doi.org/10.24432/C5M888",
                       public_snapshot_url=provenance["source_url"],revision=provenance["source_revision"],
                       sha256=digest(output),local_path=output.relative_to(ROOT).as_posix(),status="verified_source")
    with manifest.open("w",encoding="utf-8",newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=fields,lineterminator="\n"); writer.writeheader(); writer.writerows(rows)
    print(json.dumps(provenance,ensure_ascii=False))

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset",choices=["groceries","splice","all"],default="groceries")
    parser.add_argument("--offline",action="store_true")
    args=parser.parse_args()
    for dataset in (["groceries","splice"] if args.dataset=="all" else [args.dataset]):
        prepare(dataset,args.offline)
