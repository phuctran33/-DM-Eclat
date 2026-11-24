# Frequent Itemset Mining — ECLAT bằng Julia

Đồ án khai thác tập phổ biến của **Nguyễn Đức Hưng** và **Trần Thiên Phúc**.
Hai backend dùng chung DFS theo lớp tiền tố, với sorted TID lists hoặc BitVector.
Kết quả ứng dụng Groceries và Splice DNA dùng chính miner của nhóm.
[Đề HCMUS](https://hcmus-cs-ta.github.io/lab-book/data-mining/projects/itemset/) ·
[Bài báo Zaki (2000)](https://doi.org/10.1109/69.846291) ·
[Toàn văn của tác giả](https://cs.rpi.edu/~zaki/PaperDir/TKDE00.pdf)

[**Report.pdf**](docs/Report.pdf) ·
[**Mở Colab từ public main**](https://colab.research.google.com/github/phuctran33/-DM-Eclat/blob/main/notebooks/demo.ipynb) ·
[Kiến trúc](docs/ARCHITECTURE.md) · [Vấn đáp](docs/DEFENSE_GUIDE.md) ·
[Đối chiếu rubric](docs/RUBRIC_FINAL_AUDIT.md)

Để chấm hoặc vấn đáp, mở PDF và bảng đối chiếu rubric trước. Sau đó chạy
lệnh kiểm thử của đề và notebook theo hướng dẫn dưới đây.

## Chạy từ clone sạch

Cần Julia ≥1.9 và Python ≥3.11. Java ≥21 và curl dành cho kiểm chứng SPMF
và tải dữ liệu. Core ECLAT dùng Julia Base/stdlib. Ví dụ dưới đây dùng shell
Linux/macOS. Có thể chạy notebook local trên Windows với Python, Julia và Java
trong PATH hoặc đặt `ECLAT_JULIA`, `ECLAT_JAVA` thành executable tương ứng.

```bash
git clone https://github.com/phuctran33/-DM-Eclat.git
cd -- -DM-Eclat
julia --project=. -e 'using Pkg; Pkg.instantiate()'
julia --project=. scripts/mine.jl --input data/toy/basic.txt --output .tools/demo-basic.txt --minsup 40% --backend list
julia --project=. scripts/mine.jl --input data/toy/basic.txt --output .tools/demo-bitset.txt --min-count 2 --backend bitset
julia --project=. scripts/compare_spmf.jl .tools/demo-basic.txt tests/reference/spmf/basic.txt
```

Toy có 5 giao dịch, ngưỡng count 2 và 7 patterns. File input gồm các ID dương tăng
dần theo từng dòng. Hai dòng cùng nội dung vẫn là hai giao dịch. File output dùng
`1 2 #SUP: 3` cho support tuyệt đối. Xem [API](docs/API.md),
[schema](docs/SCHEMA.md) và [liên hệ paper với DFS của nhóm](docs/paper-notes.md).

## Kiểm thử và notebook

```bash
julia --project test/runtests.jl
python3 scripts/prepare_spmf.py
python3 tests/test_benchmark.py -v
python3 -m pip install -r requirements-plot.txt
python3 tests/test_plot_results.py -v
python3 tests/smoke_benchmark.py
python3 -B scripts/run_notebook.py
```

Cả lệnh của đề và `julia --project=. tests/runtests.jl` chạy cùng một bộ test,
gồm list, bitset và năm references SPMF đã commit.
Script tải SPMF **2.64b** từ nguồn chính thức và kiểm SHA-256. Notebook chạy
bảy code cells, tải dữ liệu có kiểm hash, mine lại hai ứng dụng, so với live SPMF
và audit benchmark/PDF. Mỗi lần dùng thư mục mới dưới `.tools/notebook-runs/`.
Giữ `RUN_BENCHMARKS=False` để kiểm correctness mà không lặp lại phép đo.
CI chạy Julia 1.9/1.11/1.12 và chạy notebook trên Linux.

Colab clone `main` và in source commit. Phiên M3 ngày 17/11 chạy 7/7 cells
trên Google Colab từ Git bundle. Phiên **Run all từ public main** vẫn
**NOT VERIFIED**. [Lịch sử Colab M3](docs/member-b-validation/m3/colab/README.md) ·
[Cách chạy và lưu bằng chứng](docs/planning/DELIVERY.md#colab-public-main)

## Hai ứng dụng

```bash
python3 scripts/prepare_application_data.py --dataset all
julia --project=. scripts/run_applications.jl --output .tools/applications-rerun
python3 -B scripts/verify_application_results.py --output .tools/applications-rerun --java java
python3 scripts/application_tables.py --check
```

Dùng output mới hoặc rỗng. Groceries có 9.835 giỏ và 169 items. Minsup 0,5%
và minconf 0,60 cho **1.001 itemsets và 22 luật**. Splice dùng window 25:36,
giữ 3.185/3.190 mẫu và mine **381/209/48 patterns** ở EI/IE/N. Bảng 463
candidates dùng support đếm lại trên từng lớp.
[Top-10 luật](results/applications/groceries_top10.csv) ·
[Bảng DNA](results/applications/dna_patterns.csv) ·
[Bằng chứng M2](docs/M2_MEMBER_B.md)

Nguồn ứng dụng là [snapshot Groceries pin commit](https://github.com/stedy/Machine-Learning-with-R-datasets/tree/d20658ec6d336af2d4ddb5fd72b6f677dd46136e)
và [UCI Splice](https://doi.org/10.24432/C5M888). Splice dùng mirror Đại học
Szeged, với ZIP chính thức của UCI làm nguồn dự phòng. Cả hai nguồn phải cho
cùng SHA-256 của `splice.data`. [Manifest URL, revision, license và hash](data/manifest.csv)

## Benchmark

Chess, Mushroom, Retail và T10I4D100K đều lấy từ FIMI. Retail và T10 cộng 1
cho mọi ID để giữ ID dương. Bốn file normalized có tổng 8.904.405 bytes.
File lớn nhất khoảng 3,89 MiB. Đề yêu cầu HF/Kaggle cho dữ liệu vượt kích
thước repo và không ghi ngưỡng cụ thể của môn. Nguồn FIMI đã pin hash vẫn
tái lập được. [Nguồn FIMI](https://www.cs.rpi.edu/~zaki/Workshops/FIMI/data/) ·
[Chi tiết hosting](docs/RUBRIC_FINAL_AUDIT.md#dataset-hosting)

```bash
python3 scripts/acquire_benchmarks.py
python3 scripts/review_benchmarks.py --output .tools/benchmark-review
# Đo lại khi cần, trên Linux/macOS
JULIA_NUM_THREADS=1 julia --project=. scripts/benchmark_runner.jl --output .tools/benchmark-rerun
python3 scripts/plot_results.py --results .tools/benchmark-rerun
```

Runner yêu cầu output mới/rỗng hoặc checkpoint hợp lệ khi `--resume`.
Bộ số liệu công bố có **35 cấu hình, 875 phép đo OK, 70 đối chiếu full map
khớp SPMF**. Bốn tập có sáu mức minsup, năm lần lặp. End-to-end gồm startup và
I/O cho cả ba backend. Warm read+mine so hai backend Julia cùng scope.
Peak RSS lấy từ hệ điều hành.
[Phương pháp đo](docs/experiments.md) · [Raw CSV](results/raw/benchmark_runs.csv) ·
[Correctness](results/correctness/comparisons.csv) · [Hình](results/plots/) ·
[46 hashes](results/raw/artifact_sha256.csv)

## Build báo cáo

```bash
python3 -m pip install -r requirements-report.txt
python3 scripts/application_tables.py --check
python3 scripts/build_report.py --latexmk latexmk
# Hoặc dùng Tectonic đã cài
python3 scripts/build_report.py --tectonic tectonic
```

Bản IEEE hội nghị khổ A4 có **10 trang nội dung + 1 trang tài liệu tham khảo**,
với **11 nguồn**. Clone đã có hình/bảng từ CSV. Build ghi PDF và hash nguồn sau
khi qua kiểm tra, log từng lần nằm trong `.tools/report-build/`.
[Nguồn LaTeX](docs/latex/Report.tex) · [Build metadata](docs/report-build.json)

## Stdout kiểm thử Julia cuối

**792 checks pass**, không fail, error hoặc skip trên macOS arm64,
Julia 1.10.10. CI có 10 controller tests, 6 source tests, 8 delivery tests,
1 plot test và benchmark smoke test.

<details>
<summary>Xem stdout của 16 testsets</summary>

```text
Test Summary:                     | Pass  Total  Time
SPMF I/O and canonical comparison |   14     14  1.3s
Test Summary:                           | Pass  Total  Time
Threshold boundaries and API validation |   19     19  0.0s
Test Summary:    | Pass  Total  Time
Shared schema v1 |   33     33  1.4s
Test Summary:                      | Pass  Total  Time
B: CSV and Groceries normalization |   18     18  0.8s
Test Summary:                                            | Pass  Total  Time
B: Splice normalization and independent class comparison |   24     24  0.9s
Test Summary:                                          | Pass  Total  Time
B: RFC4180 writer, record positions and rule artifacts |   12     12  0.8s
Test Summary:                                          | Pass  Total  Time
B: reject inconsistent DNA patterns and export ranking |    7      7  0.2s
Test Summary:                                      | Pass  Total   Time
B: real preprocessing CLI and supplied-pattern CLI |   11     11  12.9s
Test Summary:                                             | Pass  Total  Time
B: independently generated SPMF references and provenance |   68     68  0.2s
Test Summary:                                          | Pass  Total  Time
Edge cases, input ownership and packed-word boundaries |  267    267  1.7s
Test Summary:                                      | Pass  Total  Time
Eclat: five different databases, selected backends |   80     80  0.1s
Test Summary:                                      | Pass  Total  Time
Randomized oracle and transaction-order invariance |   80     80  0.2s
Test Summary:                                     | Pass  Total  Time
Association rules and PreparedDataset integration |   94     94  1.7s
Test Summary:                    | Pass  Total  Time
CLI round trip and failure paths |   12     12  8.5s
Test Summary:                                         | Pass  Total  Time
M2: complete mining applications and output ownership |   28     28  2.8s
Test Summary:                               | Pass  Total  Time
Exact agreement with SPMF on five databases |   25     25  0.1s
```

</details>
