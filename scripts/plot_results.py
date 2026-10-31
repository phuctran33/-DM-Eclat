"""Generate figures and report tables exclusively from measured CSV artifacts."""
import argparse
import csv
from pathlib import Path
import shutil
import tomllib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from benchlib import ROOT, NA, write_csv

LABEL = {"list": "ECLAT Basic", "bitset": "ECLAT BitVector", "spmf": "SPMF Eclat"}
COLOR = {"list": "#b34d3e", "bitset": "#176b87", "spmf": "#57853b"}
SHORT = {"chess": "Chess", "mushroom": "Mushroom", "retail": "Retail", "T10I4D100K": "T10I4D100K"}


def read_csv(path):
    with open(path) as stream:
        return list(csv.DictReader(stream))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, default=ROOT/"results")
    parser.add_argument("--report", action="store_true", help="Copy generated PDFs/tables to the LaTeX source tree")
    args = parser.parse_args()
    root = args.results
    rows = read_csv(root/"raw/summary.csv")
    stats = read_csv(ROOT/"results/raw/dataset_statistics.csv")
    config = tomllib.loads((ROOT/"configs/experiments.toml").read_text())
    comparisons = read_csv(root/"correctness/comparisons.csv")
    cases = __import__("json").loads((root/"raw/cases.json").read_text())
    plots = root/"plots"
    plots.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
                         "pdf.fonttype": 42, "savefig.dpi": 180})
    def save(fig, name):
        fig.tight_layout()
        for extension in ["pdf", "png"]:
            fig.savefig(plots/f"{name}.{extension}", bbox_inches="tight")
        plt.close(fig)
    def series(ax, data, backend, scope, xfunc, scale=1):
        selected = sorted([r for r in data if r["backend"] == backend and r["metric_scope"] == scope], key=xfunc)
        valid = [r for r in selected if int(r["n_ok"]) > 0]
        if valid:
            y = [float(r["seconds_median"])*scale for r in valid]
            err = [[(float(r["seconds_median"])-float(r["seconds_min"]))*scale for r in valid],
                   [(float(r["seconds_max"])-float(r["seconds_median"]))*scale for r in valid]]
            ax.errorbar([xfunc(r) for r in valid], y, yerr=err, label=LABEL[backend],
                        marker="o", markersize=3, capsize=2, color=COLOR[backend], linewidth=1.3)
        failed = [r for r in selected if int(r["n_ok"]) < int(r["n_runs"])]
        if failed:
            ax.text(.02,.98, "Incomplete cases: " + ", ".join(f"{xfunc(r):g} ({r['n_timeout']} timeout, {r['n_oom']} OOM, {r['n_error']} error)" for r in failed),
                    transform=ax.transAxes, va="top", fontsize=6)
        ax.grid(alpha=.2)
    for dataset in config["datasets"]:
        name = dataset["name"]
        data = [r for r in rows if r["dataset"] == name]
        fig, axes = plt.subplots(2,1,figsize=(6.6,4.8),sharex=True)
        for backend in config["backends"]:
            series(axes[0], data, backend, "end_to_end", lambda r: float(r["minsup"])*100)
        for backend in ["list", "bitset"]:
            series(axes[1], data, backend, "internal_read_mine", lambda r: float(r["minsup"])*100, 1000)
        axes[0].set(title=SHORT[name], ylabel="End-to-end time (s)")
        axes[1].set(ylabel="Warm read + mine (ms)", xlabel="Minimum support (%)")
        axes[0].legend(fontsize=8)
        axes[1].legend(fontsize=8)
        axes[1].invert_xaxis()
        save(fig, f"runtime-{name}")
    fig, axes = plt.subplots(2,2,figsize=(7,4.4))
    for ax, dataset in zip(axes.flat, config["datasets"]):
        data = sorted([r for r in rows if r["dataset"] == dataset["name"] and r["backend"] == "list"
                       and r["metric_scope"] == "end_to_end" and int(r["n_ok"]) > 0],key=lambda r:float(r["minsup"]))
        ax.plot([float(r["minsup"])*100 for r in data],[int(r["n_patterns"]) for r in data],"o-",color=COLOR["list"],markersize=3)
        ax.set(title=SHORT[dataset["name"]], xlabel="Minimum support (%)", ylabel="All frequent itemsets")
        ax.invert_xaxis(); ax.grid(alpha=.2)
    save(fig,"output-size")
    memory, performance, end_to_end = [], [], []
    for dataset in config["datasets"]:
        selected = [r for r in rows if r["dataset"] == dataset["name"] and float(r["minsup"]) == float(dataset["memory_minsup"])]
        cold = {r["backend"]: r for r in selected if r["metric_scope"] == "end_to_end" and int(r["n_ok"]) > 0}
        warm = {r["backend"]: r for r in selected if r["metric_scope"] == "internal_read_mine" and int(r["n_ok"]) > 0}
        if {"list", "bitset"} <= cold.keys():
            a,b = [float(cold[k]["peak_rss_mib_median"]) for k in ["list","bitset"]]
            memory.append(dict(dataset=dataset["name"],minsup=dataset["memory_minsup"],basic_mib=a,bitvector_mib=b,reduction_percent=100*(1-b/a)))
        if {"list", "bitset"} <= warm.keys():
            a,b = [float(warm[k]["seconds_median"]) for k in ["list","bitset"]]
            performance.append(dict(dataset=dataset["name"],minsup=dataset["memory_minsup"],min_count=warm["list"]["min_count"],
                                    basic_ms=1000*a,bitvector_ms=1000*b,speedup=a/b))
        if set(config["backends"]) <= cold.keys():
            end_to_end.append(dict(dataset=dataset["name"], **{k:float(cold[k]["seconds_median"]) for k in config["backends"]}))
    for name,data in [("memory_comparison",memory),("optimization",performance),("end_to_end_medium",end_to_end)]:
        if data:
            write_csv(root/f"raw/{name}.csv",data,data[0].keys())
    fig,ax = plt.subplots(figsize=(6.4,3.2))
    for offset,key,backend in [(-.18,"basic_mib","list"),(.18,"bitvector_mib","bitset")]:
        ax.bar([i+offset for i in range(len(memory))],[r[key] for r in memory],width=.34,label=LABEL[backend],color=COLOR[backend])
    ax.set_xticks(range(len(memory)),[SHORT[r["dataset"]] for r in memory])
    ax.set_ylabel("Process peak RSS (MiB)");ax.legend(fontsize=8);ax.grid(axis="y",alpha=.2)
    save(fig,"memory")
    for experiment,name,xlabel in [("scalability","scalability","Transactions (n)"),("length","transaction-length","Transaction width (items)")]:
        xvalues={c["dataset"]:(c["n_transactions"] if experiment=="scalability" else c["x"]) for c in cases if c["experiment"]==experiment}
        data=[r for r in rows if r["dataset"] in xvalues]
        fig,axes=plt.subplots(3,1,figsize=(6.4,5.4),sharex=True)
        for backend in config["backends"]:
            series(axes[0],data,backend,"end_to_end",lambda r:xvalues[r["dataset"]])
        for backend in ["list","bitset"]:
            series(axes[1],data,backend,"internal_read_mine",lambda r:xvalues[r["dataset"]],1000)
        selected=sorted([r for r in data if r["backend"]=="list" and r["metric_scope"]=="end_to_end" and int(r["n_ok"])>0],key=lambda r:xvalues[r["dataset"]])
        axes[2].plot([xvalues[r["dataset"]] for r in selected],[int(r["n_patterns"]) for r in selected],"o-",color="#555555",markersize=3)
        axes[0].set_ylabel("End-to-end (s)");axes[1].set_ylabel("Warm read + mine (ms)")
        axes[2].set(ylabel="Frequent itemsets",xlabel=xlabel)
        axes[0].legend(fontsize=7);axes[1].legend(fontsize=7);axes[2].grid(alpha=.2)
        save(fig,name)
    if not args.report:
        return
    figures=ROOT/"docs/latex/figures"
    generated=ROOT/"docs/latex/generated"
    figures.mkdir(exist_ok=True);generated.mkdir(exist_ok=True)
    for file in plots.glob("*.pdf"):
        shutil.copyfile(file,figures/file.name)
    def table(name,header,body):
        text="% Generated by scripts/plot_results.py from real measured CSV.\n"
        text+=header+" \\\n\\midrule\n"
        text+="\n".join(" & ".join(map(str,row))+r" \\" for row in body)+"\n"
        (generated/f"{name}.tex").write_text(text)
    table("datasets",r"CSDL & $n$ & $m$ & TB & Max & Mật độ (\%)",
          [(SHORT[r["dataset"]],r["n_transactions"],r["n_items"],f"{float(r['average_width']):.2f}",r["max_width"],f"{100*float(r['density']):.3f}") for r in stats])
    table("medium-runtime",r"CSDL & $\tau$ & Basic (ms) & BitVector (ms) & $S$",
          [(SHORT[r["dataset"]],r["min_count"],f"{r['basic_ms']:.2f}",f"{r['bitvector_ms']:.2f}",f"{r['speedup']:.2f}") for r in performance])
    table("medium-e2e",r"CSDL & Basic (s) & BitVector (s) & SPMF (s)",
          [(SHORT[r["dataset"]],*[f"{r[k]:.3f}" for k in config["backends"]]) for r in end_to_end])
    table("memory",r"CSDL & Basic (MiB) & BitVector (MiB) & Giảm (\%)",
          [(SHORT[r["dataset"]],f"{r['basic_mib']:.1f}",f"{r['bitvector_mib']:.1f}",f"{r['reduction_percent']:.1f}") for r in memory])
    body=[]
    for dataset in config["datasets"]:
        selected=[r for r in comparisons if r["dataset"]==dataset["name"]]
        body.append((SHORT[dataset["name"]],len(selected),sum(r["identical"]=="True" for r in selected),
                     sum(int(r["missing"])+int(r["extra"])+int(r["wrong_support"]) for r in selected)))
    table("correctness",r"CSDL & Đối chiếu & Khớp đủ & Sai lệch",body)
    for experiment,name in [("scalability","scalability"),("length","length")]:
        body=[]
        for case in cases:
            if case["experiment"]!=experiment:continue
            warm={r["backend"]:r for r in rows if r["dataset"]==case["dataset"] and r["metric_scope"]=="internal_read_mine" and int(r["n_ok"])>0}
            if {"list","bitset"}<=warm.keys():
                a,b=warm["list"],warm["bitset"]
                body.append((case["x"],case["n_transactions"] if experiment=="scalability" else a["min_count"],a["n_patterns"],
                             f"{1000*float(a['seconds_median']):.2f}",f"{1000*float(b['seconds_median']):.2f}"))
        header=r"Tỉ lệ (\%) & $n$ & $|F|$ & Basic (ms) & BitVector (ms)" if experiment=="scalability" else r"Width & $\tau$ & $|F|$ & Basic (ms) & BitVector (ms)"
        table(name,header,body)
    table("thresholds",r"CSDL & Minsup (\%)",
          [(SHORT[d["name"]],", ".join(f"{100*float(x):g}" for x in d["minsup"])) for d in config["datasets"]])
    print("Generated 8 figures (PDF/PNG), measured comparison CSVs and 8 LaTeX table fragments")


if __name__=="__main__":
    main()
