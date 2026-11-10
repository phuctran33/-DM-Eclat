# Trạng thái M2 B — 10/11/2026

Nhánh feat/member-b-m2-applications từ main 1f7a980, sau khi PR A/B trước được merge.

| Thành phần | Đã thực hiện | Còn lại |
|---|---|---|
| Core A và schema v1 | Giữ nguyên core/schema | Review nhóm |
| Groceries B | Hai backend: 1.001 patterns, 22 rules, top-10 và diễn giải ≥3 luật | Reviewer A nghiệm thu |
| Splice B | 381/209/48 patterns EI/IE/N, 463 comparisons, counts độc lập | Reviewer A nghiệm thu |
| Correctness ứng dụng | Hai backend khớp; 4 live SPMF maps khớp 100%; 787 Julia checks | Giữ log CI/local |
| Notebook M2 | Defaults chạy prep/miner/apps/SPMF; public Colab link, Linux CI | Xác nhận Run all trên Google Colab thực |
| Chương 3 | Bảng/kết quả mined và phân tích thực, bỏ TODO kết quả ứng dụng | Review nội dung/cân trang M3 |
| Benchmark/Chương 1–2 A | Giữ nguyên evidence đã duyệt | Nghiệm thu toàn nhóm M3 |
| Report.pdf cuối/Colab final | Chưa tuyên bố hoàn tất | M3: PDF 10–15 trang, remote cold-run, nộp bài |

Chi tiết và lệnh tái lập: docs/M2_MEMBER_B.md. Checklist kế hoạch chỉ tick sau
reviewer xác nhận; code/tests pass không thay remote Colab hoặc nghiệm thu toàn nhóm.
