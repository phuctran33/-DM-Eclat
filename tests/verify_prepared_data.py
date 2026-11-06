"""Real-data B integration audit with an independent Python oracle (no FIM).

Downloads are a separate explicit step. Julia is invoked on fresh temporary output
folders. Diagnostic DNA candidates are supplied manually, not claimed as mined.
"""
import argparse,csv,hashlib,json,os,re,subprocess,tempfile,tomllib,unicodedata
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CONTRACT=tomllib.loads((ROOT/"schemas/contracts.toml").read_text(encoding="utf-8"))

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def read_csv(path):
    with path.open(encoding="utf-8",newline="") as stream:
        reader=csv.DictReader(stream)
        return reader.fieldnames,list(reader)

def grocery_oracle():
    _,rows=read_csv(ROOT/"data/applications/groceries.csv")
    baskets=defaultdict(set);duplicates=0
    for row in rows:
        key=row["basket_id"].strip()
        label=re.sub(r"\s+"," ",unicodedata.normalize("NFC",row["item_name"]).lower().strip())
        duplicates+=label in baskets[key];baskets[key].add(label)
    labels=sorted({name for basket in baskets.values() for name in basket})
    ids={label:i for i,label in enumerate(labels,1)};keys=sorted(baskets)
    return dict(transactions=[sorted(ids[x] for x in baskets[k]) for k in keys],row_ids=keys,
                source_ids=keys,classes=[""]*len(keys),mapping=dict(enumerate(labels,1)),
                audit={("ALL","kept"):len(keys),("ALL","duplicate_item_rows_collapsed"):duplicates})

def splice_oracle():
    transactions=[];keys=[];sources=[];classes=[];kept=Counter();dropped=Counter();raw=Counter()
    with (ROOT/"data/applications/splice.data").open(encoding="utf-8",newline="") as stream:
        for line,fields in enumerate(csv.reader(stream),1):
            assert len(fields)==3
            label,source,sequence=(x.strip() for x in fields)
            label=label.upper();sequence=re.sub(r"\s+","",sequence).upper();raw[label]+=1
            assert label in {"EI","IE","N"} and len(sequence)==60
            assert all(base in "ACGTRYSWKMBDHVN" for base in sequence)
            window=sequence[24:36]
            if any(base not in "ACGT" for base in window):dropped[label]+=1;continue
            transactions.append([4*slot+"ACGT".index(base)+1 for slot,base in enumerate(window)])
            keys.append(f"splice:{line}");sources.append(source);classes.append(label);kept[label]+=1
    assert dict(raw)=={"EI":767,"IE":768,"N":1655}
    positions=[-6,-5,-4,-3,-2,-1,1,2,3,4,5,6]
    mapping={4*slot+i:f"pos={position:+d};base={base}" for slot,position in enumerate(positions) for i,base in enumerate("ACGT",1)}
    audit={(label,reason):counts[label] for label in ["EI","IE","N"] for reason,counts in [("kept",kept),("ambiguous_window",dropped)]}
    return dict(transactions=transactions,row_ids=keys,source_ids=sources,classes=classes,mapping=mapping,audit=audit,raw_counts=dict(raw))

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--julia",required=True)
    parser.add_argument("--report",type=Path,required=True)
    args=parser.parse_args();report={"scope":"B preprocessing/export; no mining implementation","schema_version":"1.0.0","datasets":{}}
    report["julia_version"]=subprocess.check_output([args.julia,"--version"],text=True).strip()
    def julia(*arguments,expected=0):
        result=subprocess.run([args.julia,"--startup-file=no",f"--project={ROOT}",*map(str,arguments)],cwd=ROOT,capture_output=True,text=True,encoding="utf-8")
        assert result.returncode==expected,(arguments,result.stdout,result.stderr)
        return result.stdout
    with tempfile.TemporaryDirectory(prefix="eclat-member-b-") as temporary:
        temporary=Path(temporary)
        for name,oracle,source in [("groceries",grocery_oracle,ROOT/"data/applications/groceries.csv"),("splice",splice_oracle,ROOT/"data/applications/splice.data")]:
            expected=oracle();first=temporary/f"{name}-first";second=temporary/f"{name}-second"
            log=julia("scripts/prepare_applications.jl",name,source,first)
            julia("scripts/prepare_applications.jl",name,source,second)
            transactions=[list(map(int,row.split())) for row in (first/"transactions.txt").read_text().splitlines()]
            assert transactions==expected["transactions"],name+": transaction mismatch"
            header,items=read_csv(first/"items.csv");assert header==CONTRACT["tables"]["items"]
            assert {int(row["item_id"]):row["item_label"] for row in items}==expected["mapping"]
            if name=="splice":
                assert all(row["item_label"]==f"pos={int(row['position']):+d};base={row['base']}" for row in items)
            else:assert all(row["position"]==row["base"]=="" for row in items)
            header,observations=read_csv(first/"observations.csv");assert header==CONTRACT["tables"]["observations"]
            assert [int(x["tid"]) for x in observations]==list(range(1,len(transactions)+1))
            for column in ["row_id","source_id","class"]:
                key={"row_id":"row_ids","source_id":"source_ids","class":"classes"}[column]
                assert [x[column] for x in observations]==expected[key]
            header,audit=read_csv(first/"preparation_audit.csv");assert header==CONTRACT["tables"]["preparation_audit"]
            assert all(x["schema_version"]=="1.0.0" and x["dataset_id"]==name for x in audit)
            assert {(x["class"],x["reason"]):int(x["count"]) for x in audit}==expected["audit"]
            hashes={p.name:digest(p) for p in first.iterdir() if p.is_file()}
            assert hashes=={p.name:digest(p) for p in second.iterdir() if p.is_file()},"Preparation is not deterministic"
            julia("scripts/prepare_applications.jl",name,source,first,expected=1)
            assert hashes=={p.name:digest(p) for p in first.iterdir() if p.is_file()},"Rejected run modified existing output"
            report["datasets"][name]=dict(n_observations=len(transactions),n_mapped_items=len(items),
                source_sha256=digest(source),output_hashes=hashes,audit=[dict(class_label=k[0],reason=k[1],count=v) for k,v in expected["audit"].items()],
                checks=["all transactions","complete mapping","all metadata","audit","CSV schemas","byte determinism","overwrite guard"],stdout=log)
        # Real-data comparison diagnostic: hand-selected GT/AG position pairs.
        # Candidate files are NOT SPMF references and NOT claimed as Eclat output.
        data=splice_oracle();candidates={"EI":(27,32),"IE":(17,23)};files=[]
        for label in ["EI","IE","N"]:
            file=temporary/f"diagnostic-{label}.txt";text=""
            if label in candidates:
                key=candidates[label];count=sum(set(key)<=set(t) for t,c in zip(data["transactions"],data["classes"]) if c==label)
                assert count>0;text=" ".join(map(str,key))+f" #SUP: {count}\n"
            file.write_text(text,encoding="utf-8");files.append(file)
        output=temporary/"dna-diagnostic.csv"
        julia("scripts/compare_dna.jl",ROOT/"data/applications/splice.data",*files,output)
        header,comparisons=read_csv(output);assert header==CONTRACT["tables"]["dna_patterns"]
        assert len(comparisons)==2
        for row in comparisons:
            key=set(map(int,row["pattern_ids"].split()))
            for label in ["EI","IE","N"]:
                denominator=sum(c==label for c in data["classes"])
                count=sum(key<=set(t) for t,c in zip(data["transactions"],data["classes"]) if c==label)
                assert int(row[f"count_{label}"])==count and int(row[f"n_{label}"])==denominator
                assert abs(float(row[f"support_{label}"])-count/denominator)<1e-14
        report["dna_comparison_diagnostic"]={"candidate_origin":"manually supplied positions, not mined","all_class_counts_verified":True,"n_candidates":2}
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("PASS all real Groceries/Splice observations, mapping, metadata, audits, CSV schemas, deterministic reruns and overwrite protection")
    print("PASS DNA comparison CLI with real-data diagnostic candidates; no FIM claim")
    for name,data in report["datasets"].items():print(name,data["n_observations"],"observations",data["n_mapped_items"],"mapped items")

if __name__=="__main__":main()
