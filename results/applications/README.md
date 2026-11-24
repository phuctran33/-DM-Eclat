# Kết quả Groceries và Splice DNA

- [Groceries top-10](groceries_top10.csv) lấy mười luật theo lift từ
  [22 luật](groceries_rules.csv), sinh trên 1.001 tập phổ biến.
- [Splice](dna_patterns.csv) có 463 ứng viên độ dài 2–4 được đếm trên
  cả ba lớp. Số tập frequent EI/IE/N lần lượt là 381/209/48.

[run.toml](run.toml) ghi config, source hashes và các artifacts.
[validation.json](validation.json) ghi đối chiếu toàn bộ map với Java SPMF.
Repo giữ tập phổ biến, mapping, audit và các bảng. Numeric transactions
và từng dòng quan sát được tạo lại từ nguồn có checksum.

Chạy [Groceries](../../notebooks/01_groceries.ipynb) hoặc
[Splice DNA](../../notebooks/02_splice_dna.ipynb) để tái lập. Có thể chạy cả
hai bằng Julia CLI từ thư mục gốc:

```bash
python3 scripts/prepare_application_data.py --dataset all
python3 scripts/prepare_spmf.py
julia --project=. scripts/run_applications.jl --output .tools/applications-new
python3 scripts/verify_application_results.py --output .tools/applications-new --java java
```

Dùng thư mục output mới cho mỗi lần chạy. Trình kiểm chứng chung đối chiếu
các bảng và pattern mới với hash công bố. [Cách nghiệm thu](../../docs/RUBRIC_FINAL_AUDIT.md)
