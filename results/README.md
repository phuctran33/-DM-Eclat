# Kết quả thực nghiệm

| Vị trí | Đọc gì |
|---|---|
| `raw/benchmark_runs.csv`, `raw/summary.csv` | 875 phép đo và các median/min–max |
| `raw/environment.json`, `raw/protocol.json`, `raw/cases.json` | Phiên bản, cấu hình, seed và hash nguồn |
| `raw/dataset_statistics.csv`, `raw/dataset_provenance.json` | Thống kê, URL, biến đổi và hash input |
| `correctness/comparisons.csv` | 70 phép so đầy đủ itemset/support |
| `raw/optimization.csv`, `raw/memory_comparison.csv`, `raw/end_to_end_medium.csv` | Bảng hiệu năng ở minsup trung bình |
| `plots/` | Tám PDF cho LaTeX. Demo vẽ PNG từ CSV vào thư mục phiên chạy |
| `applications/` | Kết quả mined, luật và top-10 Groceries, mẫu Splice và provenance |
| `logs/benchmark-logs.tar.gz` | OS RSS, stdout, stderr, lệnh chạy và hash output |

Chạy `python3 scripts/verify_artifacts.py` từ clone đầy đủ để kiểm
manifest, nguồn tại commit đo và archive. Khi cần xem log, dùng
`tar -tzf results/logs/benchmark-logs.tar.gz` để liệt kê và `tar -xOf`
để đọc một mục. [Phương pháp đo](../docs/experiments.md) ·
[Đối chiếu rubric và lịch sử](../docs/RUBRIC_FINAL_AUDIT.md)

<a id="ung-dung"></a>
## Kết quả Groceries và Splice DNA

- [Groceries top-10](applications/groceries_top10.csv) lấy mười luật theo lift từ
  [22 luật](applications/groceries_rules.csv), sinh trên 1.001 tập phổ biến.
- [Splice](applications/dna_patterns.csv) có 463 ứng viên độ dài 2–4 được đếm trên
  cả ba lớp. Số tập frequent EI/IE/N lần lượt là 381/209/48.

[run.toml](applications/run.toml) ghi config, source hashes và các artifacts.
[validation.json](applications/validation.json) ghi đối chiếu toàn bộ map với Java SPMF.
Repo giữ tập phổ biến, mapping, audit và các bảng. Numeric transactions
và từng dòng quan sát được tạo lại từ nguồn có checksum.

Chạy [Groceries](../notebooks/01_groceries.ipynb) hoặc
[Splice DNA](../notebooks/02_splice_dna.ipynb) để tái lập. Có thể chạy cả
hai bằng Julia CLI từ thư mục gốc:

```bash
python3 scripts/prepare_application_data.py --dataset all
python3 scripts/prepare_spmf.py
julia --project=. scripts/run_applications.jl --output .tools/applications-new
python3 scripts/verify_application_results.py --output .tools/applications-new --java java
```

Dùng thư mục output mới cho mỗi lần chạy. Trình kiểm chứng chung đối chiếu
các bảng và pattern mới với hash công bố. [Cách nghiệm thu](../docs/RUBRIC_FINAL_AUDIT.md)
