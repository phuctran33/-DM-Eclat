# Frequent Itemset Mining — ECLAT / Julia

Đồ án theo [đề HCMUS](https://hcmus-cs-ta.github.io/lab-book/data-mining/projects/itemset/),
Zaki (2000), *Scalable Algorithms for Association Mining*,
[DOI](https://doi.org/10.1109/69.846291).
A — Nguyễn Đức Hưng: core, tối ưu, benchmark và Chương 1–2.
B — Trần Thiên Phúc: kiểm chứng, Groceries/Splice DNA, notebook, Chương 3 và đóng gói.

## Bàn giao M3 B

- [Report.pdf](docs/Report.pdf): IEEE tiếng Việt, **10 trang nội dung + 1 trang tài liệu tham khảo**,
  đủ ba chương và 10 nguồn; [LaTeX](docs/latex/Report.tex), [hash/build metadata](docs/report-build.json).
- Groceries: **1.001 patterns, 22 luật**, top-10 theo lift, diễn giải ba luật.
  Splice EI/IE/N: **381/209/48** patterns; **463** candidates so sánh ba lớp.
- Audit A: **35 cases, 875 measurements, 70 full-map comparisons**, 46 artifact hashes nguyên vẹn.
  B chạy thêm bốn benchmark ở ngưỡng trung bình: list = BitVector = Java SPMF, khớp toàn map.
- Run all M3 local: **7/7 code cells**, **790 Julia checks**, 4 source tests,
  6 delivery-gate tests, bốn đối chiếu ứng dụng và bốn benchmark với live Java SPMF.
  [Log](docs/member-b-validation/m3/local-run-all.log), [summary](docs/member-b-validation/m3/local-summary.json),
  [bàn giao chi tiết](docs/M3_MEMBER_B.md).
- Nhánh **feat/member-b-m3-delivery** đang local, **chưa push** theo yêu cầu.
  Public main chứa M2 đã merge. [Colab M2 thực](docs/member-b-validation/colab/README.md):
  7/7 cells, Julia 1.12.6, 790 checks; giữ riêng với bằng chứng M3.

[**Mở Colab từ public main**](https://colab.research.google.com/github/phuctran33/-DM-Eclat/blob/main/notebooks/demo.ipynb).
Link này chạy M2 cho đến khi M3 được publish. Kiểm thử M3 chưa push bằng notebook
và Git bundle local theo [hướng dẫn M3](docs/M3_MEMBER_B.md).

## Chạy toàn bộ trên máy

Cần **Julia ≥1.9**, **Python ≥3.11**, **Java ≥21** cho SPMF.
Core Julia dùng Base/stdlib; Python điều phối/kiểm chứng, không có thư viện FIM.

~~~powershell
python -B scripts/run_notebook.py
~~~

VS Code trên máy đã cấu hình: chọn kernel **Eclat (Python 3.11)**.
Hoặc dùng Python 3.11+ có ipykernel. Notebook Python gọi Julia của nhóm;
tự tìm portable Julia trong .tools và Java ≥21. Có thể đặt ECLAT_JULIA/ECLAT_JAVA
thành đường dẫn executable. Mỗi lần tạo output mới trong .tools/notebook-runs.

RUN_BENCHMARK_VERIFICATION và FINAL_DELIVERY_VALIDATION mặc định True.
RUN_BENCHMARKS mặc định False: đo lại runtime/RSS là tùy chọn Linux/macOS;
không cần đo lại 875 lượt để kiểm tra bản bàn giao.

## Miner / ứng dụng

~~~bash
julia --project=. -e 'using Pkg; Pkg.instantiate()'
julia --project=. scripts/mine.jl --input data/toy/basic.txt --output results/basic.txt --minsup 0.4 --backend list
julia --project=. scripts/mine.jl --input data/toy/basic.txt --output results/bitset.txt --min-count 2 --backend bitset
python scripts/prepare_application_data.py --dataset all
julia --project=. scripts/run_applications.jl --output results/applications-rerun
python -B scripts/verify_application_results.py --output results/applications-rerun --java /path/to/java21
~~~

Output directory ứng dụng phải mới/rỗng. Miner xuất **mọi** frequent itemset/support
tuyệt đối, dạng 1 2 #SUP: 3. Input SPMF: ID dương tăng dần, không trùng item trong
transaction; giữ các transactions giống nhau. Threshold decimal/percent chính xác.
[API](docs/API.md), [schema v1](docs/SCHEMA.md), [paper notes](docs/paper-notes.md):
DFS prefix extension của nhóm là adaptation, phân biệt bottom-up trong paper.

[Kết quả CSV](results/applications/), [bàn giao M2](docs/M2_MEMBER_B.md) có mapping,
window 25:36, ambiguity, denominator riêng từng lớp, config và provenance.
Groceries: [snapshot stedy](https://github.com/stedy/Machine-Learning-with-R-datasets/tree/d20658ec6d336af2d4ddb5fd72b6f677dd46136e);
Splice: [UCI DOI](https://doi.org/10.24432/C5M888) qua mirror học thuật pin hash.
Benchmark: [FIMI](https://www.cs.rpi.edu/~zaki/Workshops/FIMI/data/),
Chess/Mushroom/Retail/T10I4D100K; Retail/T10 cộng 1 vào mọi ID.
[Manifest](data/manifest.csv), [config nguồn](configs/datasets.toml) giữ URL/license/hash.
Không commit raw data; không gọi URL học thuật là HF/Kaggle snapshot chưa xác minh.

## Tests / benchmark

~~~bash
python scripts/prepare_spmf.py --java /path/to/java21
julia --project=. tests/runtests.jl
python -B tests/test_application_sources.py
python -B tests/test_delivery.py -v
python scripts/acquire_benchmarks.py
python scripts/review_benchmarks.py --julia /path/to/julia --java /path/to/java21 --output results/new-review
~~~

SPMF **2.64b** tải từ archive chính thức, kiểm SHA-256; không commit JAR.
Full Julia bật cả list/bitset và SPMF; exhaustive/random/edge tests.
Review B so mọi itemset/support, không chỉ pattern count; không thay phép đo A.

A đo sáu minsup/dataset, năm repetitions, Retail subsets 10/25/50/75/100% và
synthetic widths 5/10/15/20/25/30, seed 42. [Raw](results/raw/benchmark_runs.csv),
[summary](results/raw/summary.csv), [correctness](results/correctness/comparisons.csv),
[plots](results/plots/), [environment](results/raw/environment.json),
[protocol](results/raw/protocol.json), [phương pháp](docs/experiments.md).
Máy đo Apple M1/macOS của A; end-to-end và warm read+mine phân tích riêng.

Đo lại trên Linux/macOS, output mới/rỗng:

~~~bash
python -m pip install -r requirements-plot.txt
julia --project=. scripts/benchmark_runner.jl --java /path/to/java21 --output results/reproduced
python scripts/plot_results.py --results results/reproduced
~~~

## Báo cáo / nghiệm thu

~~~bash
python -m pip install -r requirements-report.txt
python scripts/application_tables.py --check
python scripts/build_report.py --tectonic /path/to/tectonic
~~~

[Hướng dẫn TeX](docs/latex/README.md) có Tectonic đã kiểm và TeX Live.
Gate kiểm PDF/nguồn/số trang, bảng ứng dụng khớp CSV, số liệu A, output ứng dụng
mine mới và live SPMF. [PDF review A](docs/Member-A-review.pdf) giữ riêng.

[Checklist](docs/planning/DELIVERY.md) chỉ tick sau reviewer xác nhận.
Nhóm rà MSSV/Group ID nếu yêu cầu, hạn Moodle chính thức và public link trước nộp.
Ngày 17/11 trong kế hoạch là mốc nội bộ.

## Stdout full Julia cuối — M3 local, 17/11/2026

790 pass, không fail/error/skip. Stdout thật từ Run all local.
Log lịch sử 622 checks của A giữ tại results/logs/final-tests.log.

~~~text
Test Summary:                     | Pass  Total  Time
SPMF I/O and canonical comparison |   14     14  1.4s
Test Summary:                           | Pass  Total  Time
Threshold boundaries and API validation |   19     19  0.0s
Test Summary:    | Pass  Total  Time
Shared schema v1 |   33     33  1.4s
Test Summary:                      | Pass  Total  Time
B: CSV and Groceries normalization |   18     18  0.8s
Test Summary:                                            | Pass  Total  Time
B: Splice normalization and independent class comparison |   24     24  0.8s
Test Summary:                                          | Pass  Total  Time
B: RFC4180 writer, record positions and rule artifacts |   12     12  0.7s
Test Summary:                                          | Pass  Total  Time
B: reject inconsistent DNA patterns and export ranking |    7      7  0.1s
Test Summary:                                      | Pass  Total   Time
B: real preprocessing CLI and supplied-pattern CLI |   11     11  10.9s
Test Summary:                                             | Pass  Total  Time
B: independently generated SPMF references and provenance |   68     68  0.2s
Test Summary:                                          | Pass  Total  Time
Edge cases, input ownership and packed-word boundaries |  267    267  1.5s
Test Summary:                                      | Pass  Total  Time
Eclat: five different databases, selected backends |   80     80  0.1s
Test Summary:                                      | Pass  Total  Time
Randomized oracle and transaction-order invariance |   80     80  0.2s
Test Summary:                                     | Pass  Total  Time
Association rules and PreparedDataset integration |   94     94  1.8s
Test Summary:                    | Pass  Total  Time
CLI round trip and failure paths |   10     10  8.6s
Test Summary:                                         | Pass  Total  Time
M2: complete mining applications and output ownership |   28     28  2.5s
Test Summary:                               | Pass  Total  Time
Exact agreement with SPMF on five databases |   25     25  0.0s
~~~
