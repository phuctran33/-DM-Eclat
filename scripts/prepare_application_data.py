"""Fetch source data and adapt it to B's frozen inputs; no FIM library is used."""
import argparse,csv,hashlib,json,os,shutil,subprocess
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

def fetch(url,path,offline):
    if path.exists(): return
    if offline: raise FileNotFoundError(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    temporary=Path(str(path)+".part")
    curl=shutil.which("curl.exe") if os.name=="nt" else shutil.which("curl")
    if not curl: raise RuntimeError("curl is required for acquisition")
    subprocess.run([curl,"-fLsS","--retry","1","--connect-timeout","15","--max-time","90",url,"-o",str(temporary)],check=True)
    os.replace(temporary,path)

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
        source=cache/"splice-source.data"; fetch(SPLICE_URL,source,offline)
        if digest(source)!=SPLICE_HASH: raise ValueError("Splice pinned academic mirror checksum mismatch")
        data=source.read_bytes()
        rows=list(csv.reader(data.decode("utf-8").splitlines(),strict=True))
        if len(rows)!=3190 or any(len(row)!=3 for row in rows):
            raise ValueError("Unexpected Splice source shape")
        output=destination/"splice.data"; output.write_bytes(data)
        provenance=dict(dataset=dataset,source_url=SPLICE_URL,source_revision="sha256:"+SPLICE_HASH,
                        original_source="https://doi.org/10.24432/C5M888",original_download_url=SPLICE_ORIGINAL_URL,
                        source_kind="University of Szeged academic UCI mirror; original sample IDs preserved",
                        source_sha256=digest(source),adapter="copy raw records without modification",
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
