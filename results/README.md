# Kết quả sinh khi chạy, chưa có số liệu trong template

Gợi ý cấu trúc: `reference/`, `raw/`, `correctness/`, `figures/`, `applications/`,
`logs/`, `subsets/`, `synthetic/`. Ghi rõ backend/config/dataset revision/seed/run ID.

CSV benchmark: dataset, input_sha256, backend, minsup, min_count, repeat,
n_transactions, n_patterns, metric_scope, seconds, allocated_bytes, peak_rss_mib,
exit_status, timeout. Không điền giá trị thiếu bằng 0.

CSV ứng dụng và nội dung cần phân tích được mô tả tại `docs/applications.md`.
Thư mục này được ignore để tránh commit output lớn; chủ động đưa bảng/hình cuối
cần cho báo cáo vào `docs/latex/figures/`, kèm dữ liệu số và lệnh tái tạo.
