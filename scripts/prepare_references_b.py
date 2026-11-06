"""Generate B's five genuine SPMF references and verify against exhaustive counting.

No implementation or artifact is copied from A's feature branch.
"""
import argparse,csv,hashlib,itertools,json,os,re,shutil,subprocess,tempfile,tomllib
from pathlib import Path
from prepare_application_data import fetch,digest
ROOT=Path(__file__).resolve().parents[1]
JAR_URL="https://www.philippe-fournier-viger.com/spmf/spmf2.64.jar"
JAR_HASH="c67c2e56bdd2072eadc0e4bc96c8221cec38c9109f99c4b5f10be8eba64ec250"
NAMES=["basic","dense","sparse","duplicates","boundary"]

def patterns(path):
    result={}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line=raw.strip()
        if not line or line[0] in "#%@":continue
        left,right=line.split("#SUP:");key=tuple(sorted(map(int,left.split())));support=int(right.strip())
        if not key or len(set(key))!=len(key) or min(key)<=0 or support<=0 or key in result:
            raise ValueError(f"Invalid reference output: {path}")
        result[key]=support
    return result

def exhaustive(path):
    transactions=[set(map(int,row.split())) for row in path.read_text().splitlines() if row.strip()]
    universe=sorted(set.union(*transactions));threshold=(2*len(transactions)+4)//5;result={}
    if len(universe)>12:raise ValueError("Toy-only oracle")
    for width in range(1,len(universe)+1):
        for key in itertools.combinations(universe,width):
            count=sum(set(key)<=row for row in transactions)
            if count>=threshold:result[key]=count
    return transactions,threshold,result

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--java",default=os.environ.get("ECLAT_JAVA","java"))
    parser.add_argument("--offline",action="store_true")
    args=parser.parse_args();jar=ROOT/"tools/spmf.jar"
    if not jar.exists():
        cached=ROOT/".tools/downloads/spmf-source.jar";fetch(JAR_URL,cached,args.offline)
        if digest(cached)!=JAR_HASH:raise ValueError("Official SPMF JAR checksum mismatch")
        shutil.copyfile(cached,jar)
    if digest(jar)!=JAR_HASH:raise ValueError("Existing SPMF JAR does not match pinned 2.64b; preserving it")
    java=subprocess.run([args.java,"-version"],capture_output=True,text=True,encoding="utf-8",check=True,timeout=30)
    java_version=(java.stdout+java.stderr).splitlines()[0]
    version=subprocess.run([args.java,"-jar",str(jar),"version"],capture_output=True,text=True,encoding="utf-8",check=True,timeout=30)
    match=re.search(r"SPMF version\s+(\S+)",version.stdout+version.stderr)
    if not match:raise ValueError("SPMF version was not reported")
    evidence=ROOT/"docs/member-b-validation/spmf";evidence.mkdir(parents=True,exist_ok=True)
    fields=tomllib.loads((ROOT/"schemas/contracts.toml").read_text(encoding="utf-8"))["tables"]["spmf_manifest"]
    manifest=[];summary={"origin":"B independently generated references on main-based branch","spmf_url":JAR_URL,"spmf_sha256":JAR_HASH,"java_version":java_version,"cases":[]}
    with tempfile.TemporaryDirectory(prefix="eclat-b-spmf-") as directory:
        generated=[]
        for name in NAMES:
            source=ROOT/f"data/toy/{name}.txt";output=Path(directory)/f"{name}.txt"
            command=[args.java,"-jar",str(jar),"run","Eclat",str(source),str(output),"40%"]
            run=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,encoding="utf-8",timeout=60)
            (evidence/f"{name}.stdout.log").write_text(run.stdout,encoding="utf-8",newline="\n")
            (evidence/f"{name}.stderr.log").write_text(run.stderr,encoding="utf-8",newline="\n")
            run.check_returncode()
            transactions,threshold,expected=exhaustive(source)
            actual=patterns(output)
            if actual!=expected or patterns(ROOT/f"data/toy/{name}.expected.txt")!=expected:
                raise ValueError(f"Reference or handwritten expected differs from independent oracle: {name}")
            destination=ROOT/f"tests/reference/spmf/{name}.txt"
            raw_hash=digest(output)
            canonical=output.read_bytes().replace(b"\r\n",b"\n")
            canonical_hash=hashlib.sha256(canonical).hexdigest()
            manifest.append(dict(schema_version="1.0.0",dataset=name,input_path=source.relative_to(ROOT).as_posix(),input_sha256=digest(source),
                minsup="0.4",min_count=threshold,n_transactions=len(transactions),output_path=destination.relative_to(ROOT).as_posix(),
                output_sha256=canonical_hash,spmf_version=match[1],spmf_jar_sha256=JAR_HASH,java_version=java_version,
                command=subprocess.list2cmdline(command),status="ok"))
            summary["cases"].append(dict(dataset=name,minsup="0.4",min_count=threshold,n_patterns=len(actual),exact_matches=True,raw_output_sha256=raw_hash,output_sha256=canonical_hash,newline_normalization="CRLF to LF only"))
            generated.append((canonical,destination))
        for canonical,destination in generated:destination.write_bytes(canonical)
        with (ROOT/"tests/reference/spmf/manifest.csv").open("w",encoding="utf-8",newline="") as stream:
            writer=csv.DictWriter(stream,fieldnames=fields,lineterminator="\n");writer.writeheader();writer.writerows(manifest)
    (evidence/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"PASS: five genuine SPMF {match[1]} references equal exhaustive counts at 40%; no A miner used")
    for row in summary["cases"]:print(row)

if __name__=="__main__":main()
