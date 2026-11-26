"""Generate/check Chapter 3 tables directly from the application's published CSV."""
import argparse
import csv
import re
from benchlib import ROOT

def rows(name):
    with (ROOT/"results/applications"/name).open(encoding="utf-8",newline="") as stream:
        return list(csv.DictReader(stream))

def tex(value):
    for old,new in [("\\",r"\textbackslash{}"),("&",r"\&"),("%",r"\%"),("_",r"\_"),("#",r"\#")]:
        value=value.replace(old,new)
    return value

def format_decimal(value, places):
    return f"{value:.{places}f}".replace(".", ",")

def tables():
    top=rows("groceries_top10.csv")
    output=["% Generated from results/applications/groceries_top10.csv.",
            r"\newcommand{\TableGroceries}{%",
            r"\begin{tabular}{rp{0.51\textwidth}rrrr}",r"\toprule",
            r"Hạng & Tiền kiện $\Rightarrow$ hậu kiện & Số giỏ & Hỗ trợ (\%) & Tin cậy (\%) & Lift \\",
            r"\midrule"]
    for row in top:
        lhs=tex(row["antecedent_labels"].replace(" | ",", "))
        rhs=tex(row["consequent_labels"].replace(" | ",", "))
        metrics = (format_decimal(100 * float(row["support"]), 4),
                   format_decimal(100 * float(row["confidence"]), 2),
                   format_decimal(float(row["lift"]), 3))
        output.append(f'{row["rank"]} & {lhs} $\\Rightarrow$ {rhs} & {row["support_count"]} & '
                      + " & ".join(metrics) + r" \\")
    output += [r"\bottomrule",r"\end{tabular}%", "}", ""]
    dna=rows("dna_patterns.csv")
    ranks={1,2}
    ranks.update(int(next(row for row in dna if int(row["length"])==width)["rank"]) for width in [3,4])
    output2=["% Generated from results/applications/dna_patterns.csv. First two ranks and first lengths 3 and 4.",
             r"\newcommand{\TableSplice}{%",
             r"\begin{tabular}{rp{0.43\columnwidth}rrr}",r"\toprule",
             r"Hạng & Mẫu theo vị trí & EI & IE & N \\",r"\midrule"]
    for row in dna:
        if int(row["rank"]) not in ranks:continue
        items=[re.fullmatch(r"pos=([+-]?[0-9]+);base=([ACGT])", value).groups() for value in row["pattern_labels"].split(" | ")]
        label=r",\allowbreak ".join(f"({position},{base})" for position,base in items)
        supports = [format_decimal(100 * float(row["support_" + c]), 2) for c in ("EI", "IE", "N")]
        output2.append(f'{row["rank"]} & $' + label + '$ & ' + " & ".join(supports) + r" \\")
    output2 += [r"\bottomrule",r"\end{tabular}%", "}"]
    return {"application-tables.tex": "\n".join(output + output2) + "\n"}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check",action="store_true")
    args=parser.parse_args()
    for name,text in tables().items():
        target=ROOT/"docs/latex/generated"/name
        if args.check:
            if target.read_text("utf-8")!=text:raise ValueError(f"Stale report table: {target}")
        else:target.write_text(text,"utf-8")
    print("PASS Chapter 3 tables match source CSV" if args.check else "Generated Chapter 3 tables from CSV")

if __name__=="__main__":main()
