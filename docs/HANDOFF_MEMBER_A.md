# Bàn giao Member A — Nguyễn Đức Hưng, 31/10/2026

## A. Tổng quan

Repo: https://github.com/phuctran33/-DM-Eclat; local `/Users/nguyenduchung/-DM-Eclat`.
Branch `feat/member-a-eclat-complete`, base `e1c9865`. HEAD cuối đọc bằng
`git rev-parse HEAD`; commit đóng băng phép đo là
`49dafc999b6c00f8c4275ee68f99d4a6e3046f3d`. Hoàn thành implementation A, correctness,
BitVector/rules helper, harness, toàn bộ 35 cases và Chương 1–2. Không đánh dấu
Groceries/DNA/Chương 3/remote Colab của B đã hoàn thành.

## B. Các file thay đổi

Danh sách từng file: `docs/changed-files-member-a.txt`.

| Đường dẫn / nhóm | Nhiệm vụ và lý do |
|---|---|
| src/algorithm/baseline.jl | Vertical lists, two-pointer intersection, DFS chung, prune và all-pattern output |
| src/algorithm/bitset.jl | BitVector packed, singleton count trước cấp mask, giao có ownership riêng |
| src/applications/rules.jl | Mọi split luật, exact minconf kể cả numeric scientific notation, ranking v1 |
| scripts/mine.jl | CLI tích hợp miner thực, bỏ thông báo scaffold |
| scripts/benchmark_worker.jl | Full-case warm-up, năm internal repeats, kiểm output mỗi lần |
| scripts/benchmark_runner.jl/.py, benchlib.py | TOML grid, preflight, external wall/RSS, timeout, logs, aggregation và runtime-safe resume |
| scripts/acquire_benchmarks.py, prepare_spmf.py | Acquisition chính thức pin checksum; references SPMF thật |
| scripts/plot_results.py, verify_artifacts.py | Figures/tables từ CSV; audit schema, source snapshot và archived OS logs |
| tests/runtests.jl, test_correctness.jl, test_rules.jl, test_cli.jl | Mặc định bật mọi test A, oracle/edge/tails/ownership/rules/CLI |
| tests/test_benchmark.py, smoke_benchmark.py | Real process timeout/RSS, strict maps, bins, resume, generator/subsets |
| tests/reference/spmf/ | Năm references JAR-generated và provenance manifest |
| configs/datasets.toml, experiments.toml, data/manifest.csv | Nguồn/hash/license, grids/repeats/timeout/scalability |
| Project.toml, Manifest.toml, requirements-plot.txt | Metadata nhóm, stdlib environment và plotting dependency |
| .github/workflows/ci.yml, .gitignore | Linux Julia 1.9/1.11 correctness/smoke; giữ artifacts nhỏ, bỏ JAR/raw/cache |
| docs/paper-notes.md, API.md, SCHEMA.md, experiments.md, verification.md | Paper adaptation, trạng thái API v1, protocol, evidence thật |
| docs/latex/sections/01-implementation.tex, 02-evaluation.tex | Chương 1–2 tiếng Việt hoàn chỉnh, công thức/proof/trace/số đo/giới hạn |
| docs/latex/Report.tex, MemberAReview.tex, references.bib, figures/, generated/ | Build IEEE hai entry points; citation, hình/bảng thật |
| docs/Member-A-review.pdf | PDF review A 9 trang, không thay báo cáo cuối nhóm |
| notebooks/demo.ipynb | Chỉ nối tế bào A/miner/SPMF/benchmark; ứng dụng B không viết lại |
| README, planning/status/issues A, data/tools/reference/results READMEs | Hướng dẫn chạy, evidence và phần còn lại |
| results/raw/, correctness/, plots/, logs/, reference/ | 875 số đo thật, 70 map comparisons, plots và archive logs |

Shared `structures.jl`, `schemas.jl`, `schemas/contracts.toml` và module Groceries/DNA
của B giữ nguyên so với base. Các issue checkboxes acceptance chờ B review.

## C. ECLAT Basic

TIDs 1-based, duplicate transaction rows được giữ. Item order tăng ID, mỗi key có
một canonical prefix path. Giao sorted lists hai con trỏ không mutate parent;
support >= threshold được emit, candidate dưới threshold bị prune. API cũ trả
Vector{Pattern}, mọi frequent itemset không rỗng; writer sort length/key.
Exact rational CLI bảo toàn các boundary như 0.07 trên 100 transactions.

Oracle exhaustive độc lập: 5 fixtures, nhiều count thresholds, 20 DB ngẫu nhiên,
reverse transaction order, sparse/dense, empty/singleton, invalid input và ownership.
Năm SPMF references thật ở 40% khớp tuyệt đối cả map, không chỉ count.

## D. BitVector

Count singleton trước khi cấp bitmap n bit; AND tạo mask mới, support=count bits.
Dùng chung DFS với Basic. Test tails 63/64/65/127/128/129 TIDs và full-map equality.
Tại ngưỡng trung bình, speedup warm read+mine Basic/BitVector: Chess 5.10x,
Mushroom 1.73x, Retail 0.91x, T10I4D100K 3.12x. Không kết luận bitmap luôn thắng.

## E. Kết quả benchmark thực

35 cấu hình: 24 benchmark grid + 5 Retail subsets + 6 synthetic widths.
875 measurements = 525 end-to-end (3 backends × 5 reps) + 350 warm Julia
(2 backends × 5 reps); **875 ok, 0 timeout/OOM/error**.
70 full-map comparisons với SPMF: tất cả identical, missing/extra/wrong_support=0.

| CSDL / minsup | End-to-end Basic (s) | BitVector (s) | SPMF (s) | Warm speedup | RSS Basic/BitVector (MiB) |
|---|---:|---:|---:|---:|---:|
| Chess / 85% | 1.644 | 1.562 | 0.537 | 5.10 | 304.4 / 259.1 |
| Mushroom / 50% | 1.589 | 1.603 | 0.484 | 1.73 | 271.6 / 259.0 |
| Retail / 3% | 1.502 | 1.523 | 1.205 | 0.91 | 291.4 / 280.0 |
| T10I4D100K / 1% | 3.451 | 2.105 | 0.884 | 3.12 | 345.1 / 351.1 |

Mỗi thời gian là median 5 reps, plots dùng min–max. Warm Julia loại startup/write;
không so với SPMF ở scope khác. Peak RSS lấy BSD time, không phải allocated bytes.
RSS giảm 14.88%, 4.63%, 3.89%, và -1.74% tương ứng; chênh nhỏ chưa chứng minh hiệu
ứng ổn định trên mọi phiên. Một máy M1 8 GiB, background/frequency/cache/order chưa
được kiểm soát hoàn toàn; wait overhead có thể đến khoảng 50 ms.

Output ranges trên sáu ngưỡng: Chess 77→48731, Mushroom 51→1189, Retail 16→580,
T10 155→2001. Retail subsets có 161/157/162/158/159 patterns. Uniform widths
5/10/15/20/25/30 cho 0/0/0/53/100/100; không phải IBM/planted generator.
8 figures PDF/PNG, CSV, environment, hashes và log archive nằm trong results/.
Raw datasets và JAR không commit; dữ liệu FIMI pin raw SHA-256, Retail/T10 đổi mọi
ID bằng +1 để đáp ứng parser dương. Cùng normalized bytes cho ba backends.

## F. Report

`docs/latex/sections/01-implementation.tex`: definitions, paper/DFS distinction,
pseudocode, trace, types/API/CLI, correctness proof, BitVector, complexity/memory,
rules và tests. `02-evaluation.tex`: protocol, actual statistics, correctness,
runtime/output/RSS/scalability/length, tradeoffs/limits và ít nhất hai tối ưu tiếp.

`docs/Member-A-review.pdf`: 9 trang, A-only review. `docs/latex/Report.pdf` local:
10 trang gồm template Chương 3; không gọi là bản nộp nhóm cuối và không ghi đè
`docs/Report.pdf`. Hai entry points latexmk thành công, không undefined references,
không overfull boxes; underfull justification warnings có thể còn. Bổ sung đủ
paper gốc và nhiều nguồn liên quan, gồm attribution Retail theo yêu cầu donor.

## G. Testing

- Julia full suite: **622 pass, 0 fail/error/skip**; nguyên stdout `results/logs/final-tests.log`.
- Python controller: **5/5 methods pass**, log `controller-tests.log`.
- Real smoke: 5 measurements + 2 comparisons, log isolation, safe/runtime-guarded resume,
  deterministic synthetic và nested subsets; log `benchmark-smoke.log`.
- Local notebook code cells đã chạy với miner/BitVector bật, apps/benchmark tùy chọn
  tắt; đây không phải remote Colab cold-run.
- Artifact audit: 35 cases/875 rows/70 maps, headers/unique IDs/count bins/input hashes,
  aggregates và archived OS logs; frozen source khớp commit phép đo.
- LaTeX cả hai entry points thành công; các logs trong results/logs/.

## H. Git

Feature branch có commits theo baseline/correctness, BitVector/rules, benchmark
infrastructure, fixes và measured report/evidence. Không force-push, không merge main.
Draft PR: https://github.com/phuctran33/-DM-Eclat/pull/1. HEAD cuối báo trong
handoff chat. Dùng `git log --oneline origin/main..HEAD` xem lịch sử.

## I. Remaining blockers / việc còn lại

Không còn TODO implementation trong phạm vi A. Các việc toàn nhóm chưa hoàn thành:

1. B triển khai `src/applications/groceries.jl`, `dna.jl`, dữ liệu/mapping/audit,
   pipeline/rule CSV/DNA comparison; A đã cung cấp miner và rules helper.
2. B điền `docs/latex/sections/03-applications.tex`, kiểm notebook Colab từ runtime
   sạch, public URLs và hai ứng dụng trên dữ liệu thật; không dùng tests schema thay thế.
3. Nhóm review paper adaptation/số đo, thông tin MSSV/lớp/deadline và cân 10–15 trang
   nội dung cuối, rồi build/copy `docs/Report.pdf`.
4. Điều kiện Retail yêu cầu attribution và gửi bản nộp/final cho donor để tracking
   (URL trong data README); chưa tự gửi email vì không có chỉ thị gửi thư.

## J. Chạy lại từ đầu

Cần Julia ≥1.9 (để tái lập bản đo dùng 1.10.10), Java ≥21, Python ≥3.11, curl và
TeX Live với IEEEtran/vntex/babel-vietnamese/algorithm/algpseudocode.

```bash
git clone --branch feat/member-a-eclat-complete https://github.com/phuctran33/-DM-Eclat.git
cd -- -DM-Eclat
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-plot.txt
julia --project=. -e 'using Pkg; Pkg.instantiate()'
python scripts/prepare_spmf.py --references
julia --project=. scripts/mine.jl --input data/toy/basic.txt --output results/basic.txt --minsup 0.4 --backend list
julia --project=. scripts/mine.jl --input data/toy/basic.txt --output results/bitset.txt --min-count 2 --backend bitset
ECLAT_TEST_MINER=1 ECLAT_TEST_SPMF=1 ECLAT_TEST_BACKENDS=list,bitset julia --project=. tests/runtests.jl
python tests/test_benchmark.py -v
python tests/smoke_benchmark.py
python scripts/acquire_benchmarks.py
JULIA_NUM_THREADS=1 julia --project=. scripts/benchmark_runner.jl --output results/reproduced
python scripts/plot_results.py --results results/reproduced --report
cd docs/latex
latexmk -pdf -interaction=nonstopmode -halt-on-error MemberAReview.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error Report.tex
```

Trong workspace hiện tại Julia local ở `.tools/julia-1.10.10/bin`; có thể thêm PATH:
`export PATH="$PWD/.tools/julia-1.10.10/bin:$PATH"` từ root repo. Không đổi shell profile.
Verify evidence đã commit: `python scripts/verify_artifacts.py`; extract logs bằng
`tar -xzf results/logs/benchmark-logs.tar.gz -C results/logs`.
