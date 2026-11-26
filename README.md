# ECLAT · Khai thác tập phổ biến bằng Julia

Đồ án môn Khai phá dữ liệu và ứng dụng, HCMUS. Hai backend Sorted TID Lists và BitVector dùng chung DFS theo tiền tố. Cùng miner Julia được dùng cho hai ứng dụng.

| Thành viên | MSSV | Phụ trách chính |
|---|---|---|
| Nguyễn Đức Hưng | 24127174 | ECLAT, BitVector, hàm sinh luật, benchmark và Chương 1–2 |
| Trần Thiên Phúc | 24127506 | Oracle SPMF, tiền xử lý, hai pipeline ứng dụng, notebook và Chương 3 |

[Đề HCMUS](https://hcmus-cs-ta.github.io/lab-book/data-mining/projects/itemset/) · [Bài báo Zaki](https://doi.org/10.1109/69.846291) · [Report.pdf](docs/Report.pdf) · [Đối chiếu rubric](docs/RUBRIC_FINAL_AUDIT.md)

| Notebook | Mở trên Colab CPU | Kết quả chính |
|---|---|---|
| [Demo ECLAT](notebooks/demo.ipynb) | [Colab](https://colab.research.google.com/github/phuctran33/-DM-Eclat/blob/main/notebooks/demo.ipynb) | 5 toy, 35 cấu hình benchmark, 70 đối chiếu map và 875 phép đo |
| [Groceries](notebooks/01_groceries.ipynb) | [Colab](https://colab.research.google.com/github/phuctran33/-DM-Eclat/blob/main/notebooks/01_groceries.ipynb) | 9.835 giỏ, 1.001 tập phổ biến, 22 luật và top-10 theo lift |
| [Splice DNA](notebooks/02_splice_dna.ipynb) | [Colab](https://colab.research.google.com/github/phuctran33/-DM-Eclat/blob/main/notebooks/02_splice_dna.ipynb) | 3.185 mẫu hợp lệ, 381/209/48 tập theo EI/IE/N, 463 mẫu so sánh |

Mở từng notebook trong runtime CPU mới và chọn **Runtime → Run all**. Mỗi notebook tự cài môi trường, tải dữ liệu và in commit đang chạy. Demo đối chiếu lại với SPMF và vẽ đồ thị từ CSV đã đo. Lưu notebook có output và các JSON được in dưới `OUTPUT` để nghiệm thu. [Trạng thái Colab](docs/RUBRIC_FINAL_AUDIT.md#colab)

Ngày 26/11/2026, cả ba notebook đã chạy hết trên ba runtime Colab CPU mới. Demo qua 792 kiểm tra Julia và khớp SPMF trên 5 bộ toy và 4 benchmark. Hai ứng dụng khớp SPMF và xuất đủ hình. [Bằng chứng Run all và SHA-256](docs/validation/colab-2026-11-26.json)

## Chạy nhanh

Cần Git và Julia ≥1.9. Thêm Python ≥3.11, Java ≥21 và curl để tải dữ liệu, kiểm SPMF và chạy notebook. Miner sử dụng Julia Base và thư viện chuẩn.

```bash
git clone https://github.com/phuctran33/-DM-Eclat.git eclat
cd eclat
julia --project=. -e 'using Pkg; Pkg.instantiate()'
julia --project=. scripts/mine.jl --input data/toy/basic.txt --output .tools/basic.txt --minsup 40% --backend list
julia --project test/runtests.jl
```

Toy có 5 giao dịch, ngưỡng 2 và 7 tập phổ biến. Đổi `--backend bitset` và tên output để chạy bản BitVector, hoặc dùng `--min-count 2`. Kết quả dạng `1 2 #SUP: 3`. Lệnh trong đề gọi cùng suite với `julia --project=. tests/runtests.jl`.

<a id="kiem-thu-julia"></a>

## Kết quả kiểm thử Julia

<details>
<summary>792/792 kiểm tra trong 16 nhóm (Julia 1.10.10)</summary>

```text
$ julia --project test/runtests.jl
Test Summary:                     | Pass  Total  Time
SPMF I/O and canonical comparison |   14     14  0.8s
Test Summary:                           | Pass  Total  Time
Threshold boundaries and API validation |   19     19  0.0s
Test Summary:                    | Pass  Total  Time
CLI round trip and failure paths |   12     12  5.3s
Test Summary:                                          | Pass  Total  Time
Edge cases, input ownership and packed-word boundaries |  267    267  1.1s
Test Summary:                                      | Pass  Total  Time
Eclat: five different databases, selected backends |   80     80  0.1s
Test Summary:                                      | Pass  Total  Time
Randomized oracle and transaction-order invariance |   80     80  0.3s
Test Summary:                                             | Pass  Total  Time
B: independently generated SPMF references and provenance |   68     68  0.2s
Test Summary:                               | Pass  Total  Time
Exact agreement with SPMF on five databases |   25     25  0.0s
Test Summary:    | Pass  Total  Time
Shared schema v1 |   33     33  1.3s
Test Summary:                                     | Pass  Total  Time
Association rules and PreparedDataset integration |   94     94  1.6s
Test Summary:                      | Pass  Total  Time
B: CSV and Groceries normalization |   18     18  0.5s
Test Summary:                                            | Pass  Total  Time
B: Splice normalization and independent class comparison |   24     24  0.5s
Test Summary:                                          | Pass  Total  Time
B: RFC4180 writer, record positions and rule artifacts |   12     12  0.4s
Test Summary:                                          | Pass  Total  Time
B: reject inconsistent DNA patterns and export ranking |    7      7  0.1s
Test Summary:                                      | Pass  Total  Time
B: real preprocessing CLI and supplied-pattern CLI |   11     11  7.2s
Groceries: 7 frequent patterns, 9 rules, min_count=2
Splice EI: 3 patterns, min_count=3
Splice IE: 3 patterns, min_count=3
Splice N: 0 patterns, min_count=3
DNA comparisons: 2
Groceries: 7 frequent patterns, 9 rules, min_count=2
Test Summary:                                         | Pass  Total  Time
M2: complete mining applications and output ownership |   28     28  1.2s
```

</details>

## Chạy notebook và kiểm chứng

Trong môi trường Python riêng, cài các gói sau rồi chạy ba kernel mới. Trên Jupyter có thể mở từng notebook từ checkout và chọn **Restart Kernel and Run All**. Nếu Julia hoặc Java chưa ở PATH, đặt `ECLAT_JULIA` hay `ECLAT_JAVA` tới executable.

```bash
python3 -m pip install -r requirements-notebook.txt
python3 scripts/run_notebook.py
```

Log, notebook đã chạy, bảng và `delivery-validation.json` nằm trong thư mục được in ở cuối. Bước cuối so hai kết quả mới với các bảng công bố, kiểm benchmark và PDF. Dùng `--notebook notebooks/01_groceries.ipynb` nếu chỉ cần một notebook. Có thể chạy pipeline Julia riêng cho từng ứng dụng với `scripts/run_applications.jl --dataset groceries|splice --output THƯ_MỤC_MỚI` sau khi tải nguồn tương ứng bằng `scripts/prepare_application_data.py`. [Hai kết quả công bố](results/README.md#ung-dung)

<a id="benchmark"></a>
## Benchmark

Script tải bốn bộ benchmark từ FIMI tại RPI, thử tiếp kho Đại học Antwerp và các bản SPMF đã xác minh. Mỗi input phải khớp SHA-256 sau chuẩn hóa với lần đo gốc. `prepare_spmf.py` tải JAR SPMF 2.64b, kiểm phiên bản và SHA-256 để đối chiếu kết quả Julia. `python3 scripts/verify_artifacts.py` kiểm CSV, hình và log có trong checkout hiện tại. Thêm `--history` trong clone đầy đủ để đối chiếu cả tệp đã lưu trữ và mã gốc của lần đo. Để đo lại trên Linux/macOS, dùng môi trường đã cài gói vẽ và chạy các lệnh sau. [Trang SPMF](https://www.philippe-fournier-viger.com/spmf/)

```bash
python3 scripts/prepare_spmf.py
python3 scripts/acquire_benchmarks.py
JULIA_NUM_THREADS=1 python3 scripts/benchmark_runner.py --output .tools/benchmark-new
python3 scripts/plot_results.py --results .tools/benchmark-new
```

Dùng thư mục mới, hoặc `--resume` với checkpoint tương thích. Mac M1 ở lần đo công bố là một cấu hình tham chiếu. Chess tăng tốc warm 5,10× và giảm peak RSS 14,9% tại ngưỡng trung bình. Retail đạt 0,91× ở phép đo warm và BitVector dùng RSS cao hơn Basic trên T10I4D100K. [Phương pháp và giới hạn](docs/experiments.md) · [CSV và đồ thị](results/README.md)

## Nguồn dữ liệu

- Demo lưu URL thực tế, offset và checksum của Chess, Mushroom, Retail và T10I4D100K trong `dataset-acquisition.json`. Điều kiện Retail yêu cầu ghi nguồn và gửi bản nộp đầu cùng bản cuối cho bên cung cấp. [URL tải và hash chuẩn hóa](data/README.md#benchmark)
- Groceries dùng snapshot Git có revision và checksum. Splice dùng bộ UCI có giấy phép CC BY 4.0, tải bản học thuật hoặc ZIP UCI với cùng checksum. Mỗi notebook ứng dụng lưu `dataset-source.json`. [Nguồn ứng dụng](data/README.md#ung-dung) · [Manifest lịch sử](data/manifest.csv)
<a id="build-bao-cao"></a>

## Build báo cáo

Cần Python ≥3.11 và TeX Live với XeLaTeX, latexmk, IEEEtran, babel-vietnamese, TeX Gyre, booktabs, placeins, algorithm và algpseudocode. Từ thư mục gốc:

```bash
python3 -m pip install -r requirements-report.txt
python3 scripts/application_tables.py --check
python3 scripts/build_report.py --latexmk latexmk
```

Hình PDF lấy từ `results/plots/`. Các bảng sinh từ CSV đặt trong hai file LaTeX theo chương. Bước build kiểm trang, trích dẫn, font và tràn khung. Log nằm ở `.tools/report-build/`. Ngày và trình biên dịch có thể làm thay đổi byte PDF. [Nguồn LaTeX](docs/latex/) · [Hash bản phát hành](docs/report-build.json)

## Cấu trúc

| Vị trí | Nội dung |
|---|---|
| `src/` | Module Julia, hai backend, parser, tiền xử lý và ứng dụng |
| `scripts/`, `configs/` | CLI, benchmark, kiểm chứng, build báo cáo và tham số |
| `test/`, `tests/` | Lệnh test trong đề, suite Julia/Python và toy SPMF |
| `notebooks/` | Ba notebook Python gọi Julia và một file setup chung |
| `results/`, `docs/` | Bằng chứng thực nghiệm, báo cáo và tài liệu |

Để ôn vấn đáp, đọc mục tiêu và luồng ECLAT, rồi chọn một kết quả benchmark và một kết quả ứng dụng để giải thích quyết định thiết kế. [Kiến trúc](docs/ARCHITECTURE.md) · [Câu hỏi vấn đáp](docs/DEFENSE_GUIDE.md)
