"""Build the three-chapter IEEE report and validate its PDF and provenance."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from benchlib import ROOT, sha256

def report_sources(root=ROOT):
    paths=sorted(p for p in (root/"docs/latex").rglob("*")
                 if p.is_file() and p.suffix in {".tex",".bib",".pdf"}
                 and not p.name.startswith("MemberA") and not (p.parent==root/"docs/latex" and p.suffix==".pdf"))
    return {p.relative_to(root).as_posix():sha256(p) for p in paths}

def inspect_pdf(path):
    from pypdf import PdfReader
    reader=PdfReader(path)
    texts=[page.extract_text() or "" for page in reader.pages]
    text="\n".join(texts)
    for chapter in [1,2,3]:
        if not re.search(rf"Chương\s*{chapter}\s*:",text,re.I):
            raise ValueError(f"Missing Vietnamese chapter {chapter}")
    if any(marker in text for marker in ["[TODO","[?]","\ufffd"]):
        raise ValueError("Draft placeholder, unresolved reference, or invalid glyph in PDF")
    # References start on a dedicated page; count body pages independently.
    references=next((i for i,t in enumerate(texts)
                     if re.match(r"\s*(?:\d+\s*)?(?:TÀI\s*LIỆU|Tài\s*liệu|REFERENCES)",t)),None)
    if references is None:raise ValueError("Cannot find references page")
    if not 10<=references<=15:raise ValueError(f"Body is {references} pages; expected 10–15")
    # pypdf may extract bibliography labels in the opposite column order.
    if len(re.findall(r"\[\d+\]", "\n".join(texts[references:])))<4:
        raise ValueError("Fewer than four references")
    return dict(pdf_pages=len(texts),body_pages=references,reference_start_page=references+1)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    engine=parser.add_mutually_exclusive_group()
    engine.add_argument("--tectonic",default=os.environ.get("ECLAT_TECTONIC","tectonic"))
    engine.add_argument("--latexmk",metavar="EXECUTABLE",help="Use installed XeLaTeX through latexmk")
    args=parser.parse_args()
    executable=args.latexmk or args.tectonic
    compiler=shutil.which(executable)
    if compiler is None:
        parser.error(f"Compiler executable not found: {executable}")
    compiler=str(Path(compiler).resolve())
    env={**os.environ,"TECTONIC_CACHE_DIR":str(ROOT/".tools/tectonic-cache")}
    parent=ROOT/".tools/report-build";parent.mkdir(parents=True,exist_ok=True)
    work=Path(tempfile.mkdtemp(prefix="build-",dir=parent))
    if args.latexmk:
        version=subprocess.check_output(["xelatex","--version"],text=True).splitlines()[0]
        command=[compiler,"-xelatex","-interaction=nonstopmode","-halt-on-error",
                 f"-outdir={work}","Report.tex"]
    else:
        version=subprocess.check_output([compiler,"--version"],text=True).strip()
        command=[compiler,"--keep-logs","--keep-intermediates","--outdir",str(work),"Report.tex"]
    sources=report_sources()
    process=subprocess.run(command,cwd=ROOT/"docs/latex",env=env,capture_output=True)
    log=(process.stdout+process.stderr).decode("utf-8",errors="replace")
    # Keep new build logs next to the intermediates. Historical logs are hashed.
    build_log=work/"compiler.log"
    build_log.write_text(log,encoding="utf-8")
    print("Build log:",build_log,flush=True)
    print(log[-5000:],flush=True)
    process.check_returncode()
    texlog=(work/"Report.log").read_text("utf-8",errors="replace")
    if re.search(r"undefined (?:references|citations)|Citation .* undefined|Reference .* undefined|Missing character:|could not represent character|Overfull \\[hv]box",texlog,re.I):
        raise ValueError("Unresolved citation/reference, missing glyph or overflowing box; see report build log")
    info=inspect_pdf(work/"Report.pdf")
    if report_sources()!=sources:
        raise ValueError("Report source changed during compilation; rebuild")
    destination=ROOT/"docs/Report.pdf";shutil.copyfile(work/"Report.pdf",destination)
    record=dict(status="pass",compiler=version,pdf_sha256=sha256(destination),
                source_sha256=sources,**info)
    (ROOT/"docs/report-build.json").write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n","utf-8")
    print("PASS Report.pdf",info,"SHA256",record["pdf_sha256"],flush=True)

if __name__=="__main__":main()
