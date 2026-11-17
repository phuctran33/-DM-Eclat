"""Execute every notebook code cell in order, with a real Python/Julia runtime.

Used locally and by Ubuntu CI; a Linux run is not labelled a Google Colab session.
"""
import argparse,json,os
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--notebook",type=Path,default=ROOT/"notebooks/demo.ipynb")
    args=parser.parse_args()
    os.chdir(ROOT)
    nb=json.loads(args.notebook.read_text(encoding="utf-8"))
    namespace={"__name__":"__main__"}
    completed=[]
    for cell in nb["cells"]:
        if cell["cell_type"]!="code":continue
        print("EXECUTE",cell["id"],flush=True)
        exec(compile("".join(cell["source"]),cell["id"],"exec"),namespace)
        completed.append(cell["id"])
    print("PASS",len(completed),"actual notebook code cells; runtime=local/CI, not remote Colab",flush=True)
if __name__=="__main__":main()
