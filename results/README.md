# Kết quả thực nghiệm

| Vị trí | Đọc gì |
|---|---|
| `raw/benchmark_runs.csv`, `raw/summary.csv` | 875 phép đo và các median/min–max |
| `raw/environment.json`, `raw/protocol.json`, `raw/cases.json` | Phiên bản, cấu hình, seed và hash nguồn |
| `raw/dataset_statistics.csv`, `raw/dataset_provenance.json` | Thống kê, URL, biến đổi và hash input |
| `correctness/comparisons.csv` | 70 phép so đầy đủ itemset/support |
| `raw/optimization.csv`, `raw/memory_comparison.csv`, `raw/end_to_end_medium.csv` | Bảng hiệu năng ở minsup trung bình |
| `plots/` | PNG cho notebook, PDF cho LaTeX |
| `applications/` | Kết quả mined, luật và top-10 Groceries, mẫu Splice và provenance |
| `logs/benchmark-logs.tar.gz` | OS RSS, stdout, stderr, lệnh chạy và hash output |

Chạy `python3 scripts/verify_artifacts.py` từ clone đầy đủ để kiểm
manifest, nguồn tại commit đo và archive. Khi cần xem log, dùng
`tar -tzf results/logs/benchmark-logs.tar.gz` để liệt kê và `tar -xOf`
để đọc một mục. [Phương pháp đo](../docs/experiments.md) ·
[Đối chiếu rubric và lịch sử](../docs/RUBRIC_FINAL_AUDIT.md)
