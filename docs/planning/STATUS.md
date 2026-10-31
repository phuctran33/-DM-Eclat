# Trạng thái triển khai Member A — 31/10/2026

| Thành phần | Trạng thái / bằng chứng | Tiếp theo |
|---|---|---|
| Schema A/B v1.0.0 | Giữ nguyên contracts/types; tests validation pass | B dùng cùng PreparedDataset/Pattern |
| Basic sorted-list DFS | Đã triển khai; brute-force + SPMF exact, CLI | B review adaptation/prefix proof |
| BitVector | DFS chung; ownership/word-tail tests; khớp list/SPMF | Review kết quả dense/sparse |
| Rules helper | Mọi split, exact minconf, subset validation, ranking | B nối mapping/CSV ứng dụng |
| Toy/SPMF references | 5 JAR-generated references, hashes/commands/logs | Không thay bằng expected tự tính |
| Benchmark acquisition/harness | 4 FIMI datasets pin hashes; controller/RSS/timeout/aggregation | Xem CSV/logs thực trong results/ |
| Experiments/plots | Protocol trong docs/experiments.md; figures/tables từ CSV | B review số liệu và giới hạn |
| Chương 1–2 | Nguồn hoàn chỉnh; PDF review riêng | B phản biện và cân trang bản nhóm |
| Groceries preprocessing | TODO thuộc B, không sửa pipeline | Canonical CSV → PreparedDataset |
| DNA preprocessing/comparison | TODO thuộc B, mapping 25:36/48 IDs không đổi | Implement/audit rồi chạy ứng dụng |
| Chương 3 | Template của B, không đánh dấu xong | B điền kết quả thật |
| Colab | Tế bào A nối CLI/runner thật; chưa remote cold-run | B hoàn tất setup/data/apps/cold-run |
| Report.pdf cuối, nghiệm thu M2/M3 | Chưa hoàn thành toàn nhóm | Hai ứng dụng, Ch.3, public cold-run và review |

Các local issue briefs chỉ được tick nghiệm thu sau reviewer kiểm chứng theo quy
ước nhóm. Implementation/test evidence của A không tự thay cho A/B acceptance.
Đọc docs/HANDOFF_MEMBER_A.md, docs/verification.md và kết quả thực tế; không đánh
dấu gate toàn nhóm đã qua chỉ vì phần miner/benchmark chạy được.
