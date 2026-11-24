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

Mở từng notebook rồi chọn **Runtime → Run all**. Mỗi notebook tự thiết lập, in commit và ghi kết quả mới vào thư mục riêng. Demo hiển thị đồ thị từ các phép đo đã lưu và chạy mới phần so khớp SPMF. [Trạng thái Colab](docs/RUBRIC_FINAL_AUDIT.md#colab)

## Chạy nhanh

Cần Git và Julia ≥1.9. Thêm Python ≥3.11, Java ≥21 và curl để tải dữ liệu, kiểm SPMF và chạy notebook. Miner sử dụng Julia Base và thư viện chuẩn.

```bash
git clone https://github.com/phuctran33/-DM-Eclat.git eclat
cd eclat
julia --project=. -e 'using Pkg; Pkg.instantiate()'
julia --project=. scripts/mine.jl --input data/toy/basic.txt --output .tools/basic.txt --minsup 40% --backend list
julia --project test/runtests.jl
```

Toy có 5 giao dịch, ngưỡng 2 và 7 tập phổ biến. Đổi `--backend bitset` và tên output để chạy bản BitVector, hoặc dùng `--min-count 2`. Kết quả dạng `1 2 #SUP: 3`. Lệnh trong đề gọi cùng suite với `julia --project=. tests/runtests.jl`. [Stdout Julia của lần kiểm cuối](docs/validation/julia-tests.txt)

## Chạy notebook và kiểm chứng

Trong môi trường Python riêng, cài các gói sau rồi chạy ba kernel mới. Trên Jupyter có thể mở từng notebook từ checkout và chọn **Restart Kernel and Run All**. Nếu Julia hoặc Java chưa ở PATH, đặt `ECLAT_JULIA` hay `ECLAT_JAVA` tới executable.

```bash
python3 -m pip install -r requirements-notebook.txt
python3 scripts/run_notebook.py
```

Log, notebook đã chạy, bảng và `delivery-validation.json` nằm trong thư mục được in ở cuối. Bước cuối so hai kết quả mới với các bảng công bố, kiểm benchmark và PDF. Dùng `--notebook notebooks/01_groceries.ipynb` nếu chỉ cần một notebook. Có thể chạy pipeline Julia riêng cho từng ứng dụng với `scripts/run_applications.jl --dataset groceries|splice --output THƯ_MỤC_MỚI` sau khi tải nguồn tương ứng bằng `scripts/prepare_application_data.py`. [Hai kết quả công bố](results/applications/)

<a id="benchmark"></a>
## Benchmark

Bốn nguồn FIMI được pin SHA-256. Audit lại các phép đo, logs và nguồn Git bằng `python3 scripts/verify_artifacts.py`. Muốn đo lại trên Linux/macOS, từ môi trường đã cài gói vẽ chạy:

```bash
python3 scripts/prepare_spmf.py
python3 scripts/acquire_benchmarks.py
JULIA_NUM_THREADS=1 python3 scripts/benchmark_runner.py --output .tools/benchmark-new
python3 scripts/plot_results.py --results .tools/benchmark-new
```

Dùng thư mục mới, hoặc `--resume` với checkpoint tương thích. Mac M1 ở lần đo công bố là một cấu hình tham chiếu. Chess tăng tốc warm 5,10× và giảm peak RSS 14,9% tại ngưỡng trung bình. Retail đạt 0,91× ở phép đo warm và BitVector dùng RSS cao hơn Basic trên T10I4D100K. [Phương pháp và giới hạn](docs/experiments.md) · [CSV và đồ thị](results/README.md)

## Dữ liệu và báo cáo

- Chess, Mushroom, Retail và T10I4D100K được tải từ FIMI. File chuẩn hóa lớn nhất khoảng 3,89 MiB. Repo lưu link và checksum. Điều kiện Retail yêu cầu ghi nguồn và gửi bản nộp đầu cùng bản cuối cho bên cung cấp. [Nguồn benchmark](data/benchmark/README.md)
- Groceries dùng snapshot Git có revision và checksum. Splice dùng bộ UCI có giấy phép CC BY 4.0, tải bản học thuật hoặc ZIP UCI với cùng checksum. [Nguồn ứng dụng](data/applications/README.md) · [Manifest](data/manifest.csv)
- Báo cáo nằm ở `docs/Report.pdf`. Để build bằng XeLaTeX, cài TeX Live theo hướng dẫn, rồi chạy `python3 -m pip install -r requirements-report.txt` và `python3 scripts/build_report.py --latexmk latexmk`. [LaTeX](docs/latex/README.md)

## Cấu trúc

| Vị trí | Nội dung |
|---|---|
| `src/` | Module Julia, hai backend, parser, tiền xử lý và ứng dụng |
| `scripts/`, `configs/` | CLI, benchmark, kiểm chứng, build báo cáo và tham số |
| `test/`, `tests/` | Lệnh test trong đề, suite Julia/Python và toy SPMF |
| `notebooks/` | Ba notebook Python gọi Julia và một file setup chung |
| `results/`, `docs/` | Bằng chứng thực nghiệm, báo cáo và tài liệu |

Để ôn vấn đáp, chạy toy, tự tính giao TID rồi lần kết quả theo [Kiến trúc](docs/ARCHITECTURE.md). Tiếp theo đọc hai phạm vi đo và đối chiếu một luật Groceries hoặc một mẫu Splice. [Câu hỏi vấn đáp](docs/DEFENSE_GUIDE.md)
