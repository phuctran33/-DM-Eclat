# Kết quả ứng dụng M2 B

Groceries: 1.001 tập phổ biến, 22 luật, top-10 theo schema ranking.
Splice: EI/IE/N 381/209/48 tập; 463 candidates dài 2–4, đếm lại mọi lớp.
Đây là output mined thật của nhóm, được đối chiếu toàn map hai backend và
Java SPMF 2.64b. Xem run.toml, validation.json và verification/* logs.

Patterns/CSV/mapping/audit và metadata được commit. Raw data, per-observation
metadata và normalized transaction files được ignore để không nhân bản dữ liệu.
Muốn chạy auditor từ clone mới, tái tạo một output directory mới trước:

```text
python scripts/prepare_application_data.py --dataset all
julia --project=. scripts/run_applications.jl --output results/applications-rerun
python -B scripts/verify_application_results.py --output results/applications-rerun --java PATH_TO_JAVA_21
```

Không chạy đè results/applications. Metadata checksum các file đầy đủ trước khi
ignore; môi trường/runtime/provenance có thể khác nhưng các CSV/pattern outputs
phải có cùng hashes. Hai full runs local đã kiểm điều này.
Phân tích và cách tái lập đầy đủ: docs/M2_MEMBER_B.md.
