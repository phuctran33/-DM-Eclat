"""Independent count/rule audit, optionally verified against four live Java SPMF runs.

No Python FIM implementation/library: validate the emitted candidates directly.
SPMF establishes completeness of the group's entire frequent output.
"""
import argparse
import csv
import hashlib
import itertools
import json
from pathlib import Path
import subprocess
import sys
import tomllib
from decimal import Decimal
from fractions import Fraction

ROOT=Path(__file__).resolve().parents[1]
JAR_HASH="c67c2e56bdd2072eadc0e4bc96c8221cec38c9109f99c4b5f10be8eba64ec250"

def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def table(path):
    with Path(path).open(encoding="utf-8",newline="") as f:
        reader=csv.DictReader(f);return reader.fieldnames,list(reader)
def patterns(path):
    result={}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip(): continue
        items,number=line.split("#SUP:")
        key=tuple(sorted(map(int,items.split())));count=int(number)
        assert key and len(set(key))==len(key) and min(key)>0 and count>0
        assert key not in result
        result[key]=count
    return result
def transactions(path):return [set(map(int,line.split())) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]
def counter(rows):
    vertical={}
    for i,row in enumerate(rows):
        for item in row: vertical.setdefault(item,set()).add(i)
    def count(key):return len(set.intersection(*(vertical.get(item,set()) for item in key)))
    return count

def verify(output,java=None,jar=None):
    output=Path(output).resolve()
    meta=tomllib.loads((output/"run.toml").read_text(encoding="utf-8"))
    contract=tomllib.loads((ROOT/"schemas/contracts.toml").read_text(encoding="utf-8"))
    for path,expected in meta["artifact_sha256"].items():assert digest(output/path)==expected,path
    for path,expected in meta["source_sha256"].items():assert digest(ROOT/path)==expected,path
    for name,cfg in [("groceries","groceries"),("splice","dna")]:
        assert digest(ROOT/meta["config"][cfg]["input"])==meta["input_sha256"][name]
    cases=[("groceries",output/"prepared/groceries/transactions.txt",meta["statistics"]["groceries"])]
    cases += [("splice_"+label,output/f"prepared/splice/transactions_{label}.txt",meta["statistics"]["dna"]["classes"][label]) for label in ["EI","IE","N"]]
    maps={};counts={};report={"status":"pass","cases":{},"checks":["artifact/source/input hashes","all emitted supports","complete rule splits and metrics","top-10 prefix and ranking","complete DNA candidate union and recounted supports"],"spmf":[]}
    for name,path,stats in cases:
        rows=transactions(path);own=patterns(output/f"patterns/{name}.txt");count=counter(rows)
        assert len(rows)==stats["n_transactions"] and len(own)==stats["n_patterns"]
        assert all(value==count(key) and value>=stats["min_count"] for key,value in own.items())
        maps[name]=own;counts[name]=count
        report["cases"][name]={"n_transactions":len(rows),"min_count":stats["min_count"],"n_patterns":len(own)}
    n=meta["statistics"]["groceries"]["n_transactions"];own=maps["groceries"]
    confidence=Fraction(meta["config"]["groceries"]["minconf"])
    expected={}
    for union,joint in own.items():
        for width in range(1,len(union)):
            for antecedent in itertools.combinations(union,width):
                consequent=tuple(x for x in union if x not in antecedent)
                na,nb=own[antecedent],own[consequent]
                if Fraction(joint,na)>=confidence:expected[antecedent,consequent]=(joint,na,nb)
    header,rules=table(output/"groceries_rules.csv");assert header==contract["tables"]["groceries_rules"]
    labels={int(r["item_id"]):r["item_label"] for r in table(output/"prepared/groceries/items.csv")[1]}
    actual={};keys=[]
    for rank,r in enumerate(rules,1):
        a=tuple(map(int,r["antecedent_ids"].split()));b=tuple(map(int,r["consequent_ids"].split()))
        key=a,b;assert key not in actual and not set(a)&set(b)
        values=tuple(int(r[k]) for k in ["support_count","antecedent_count","consequent_count"])
        assert values==expected[key] and int(r["rank"])==rank and int(r["n_transactions"])==n
        assert values==(counts["groceries"](tuple(sorted(a+b))),counts["groceries"](a),counts["groceries"](b))
        joint,na,nb=values
        metrics=joint/n,joint/na,(joint/na)/(nb/n)
        assert all(abs(float(r[k])-v)<1e-12 for k,v in zip(["support","confidence","lift"],metrics))
        assert int(r["length"])==len(a)+len(b)
        assert r["antecedent_labels"]==" | ".join(labels[x] for x in a)
        assert r["consequent_labels"]==" | ".join(labels[x] for x in b)
        keys.append((-float(r["lift"]),-float(r["confidence"]),-float(r["support"]),len(a)+len(b),a,b));actual[key]=values
    assert actual==expected and keys==sorted(keys)
    header,top=table(output/"groceries_top10.csv")
    assert header==contract["tables"]["groceries_rules"] and top==rules[:meta["config"]["groceries"]["top_k"]]
    assert len(rules)==meta["statistics"]["groceries"]["n_rules"]
    header,dna=table(output/"dna_patterns.csv");assert header==contract["tables"]["dna_patterns"]
    expected_candidates={p for name,m in maps.items() if name!="groceries" for p in m if 2<=len(p)<=4}
    actual_candidates=set();keys=[];infrequent_nonzero=0
    dna_labels={int(r["item_id"]):r["item_label"] for r in table(output/"prepared/splice/items.csv")[1]}
    for rank,r in enumerate(dna,1):
        key=tuple(map(int,r["pattern_ids"].split()));assert key not in actual_candidates;actual_candidates.add(key)
        assert int(r["rank"])==rank and int(r["length"])==len(key)
        assert len({(item-1)//4 for item in key})==len(key)
        assert r["pattern_labels"]==" | ".join(dna_labels[x] for x in key)
        supports=[]
        for label in ["EI","IE","N"]:
            case="splice_"+label;den=report["cases"][case]["n_transactions"];count=counts[case](key)
            assert int(r["count_"+label])==count and int(r["n_"+label])==den
            assert abs(float(r["support_"+label])-count/den)<1e-14
            supports.append(count/den)
            if key not in maps[case] and count>0:infrequent_nonzero+=1
        span=max(supports)-min(supports);assert abs(float(r["support_span"])-span)<1e-14
        keys.append((-span,-max(supports),len(key),key))
    assert actual_candidates==expected_candidates and keys==sorted(keys)
    assert len(dna)==meta["statistics"]["dna"]["n_comparisons"]
    report.update(n_rules=len(rules),n_top_rules=len(top),n_dna_candidates=len(dna),nonzero_infrequent_class_counts=infrequent_nonzero)
    if java:
        jar=Path(jar or ROOT/"tools/spmf.jar").resolve();assert digest(jar)==JAR_HASH
        verification=output/"verification";verification.mkdir(exist_ok=True)
        java_version=subprocess.run([java,"-version"],capture_output=True,text=True,check=True).stderr.strip()
        for name,path,stats in cases:
            destination=verification/(name+".txt")
            # Strictly inside the same absolute-count bin, avoiding SPMF double boundaries.
            threshold=str(Decimal(2*stats["min_count"]-1)/Decimal(2*stats["n_transactions"]))
            cmd=[java,"-jar",str(jar),"run","Eclat",str(path),str(destination),threshold]
            run=subprocess.run(cmd,capture_output=True,timeout=180)
            (verification/(name+".stdout.log")).write_bytes(run.stdout)
            (verification/(name+".stderr.log")).write_bytes(run.stderr)
            assert run.returncode==0,(name,run.stderr)
            reference=patterns(destination);assert maps[name]==reference,(name,"SPMF mismatch")
            record=dict(dataset=name,n_patterns=len(reference),exact_match_rate=1.0,identical=True,
                        jar_sha256=JAR_HASH,java_version=java_version,command=cmd,
                        output_sha256=digest(destination),input_sha256=digest(path),threshold_argument=threshold)
            report["spmf"].append(record)
            print("SPMF PASS",name,len(reference),flush=True)
    print("PASS independent complete rule/DNA count audit:",len(rules),"rules;",len(dna),"DNA candidates;",infrequent_nonzero,"nonzero infrequent class counts",flush=True)
    return report

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=ROOT/"results/applications")
    parser.add_argument("--java",help="Run pinned live SPMF with this Java >=21 executable")
    parser.add_argument("--jar",type=Path)
    parser.add_argument("--report",type=Path)
    args=parser.parse_args()
    report=verify(args.output,args.java,args.jar)
    destination=args.report or args.output/"validation.json"
    destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
