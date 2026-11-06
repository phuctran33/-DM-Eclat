# Trạng thái tích hợp A/B — 05/11/2026

A đã được merge vào main qua PR #1 (`b821235`); B cập nhật main để giải quyết
conflict PR #3. Các bằng chứng lịch sử A/B được giữ riêng theo ngày và runtime.

| Thành phần | Trạng thái | Tiếp theo |
|---|---|---|
| Schema A/B v1.0.0 | Giữ nguyên contracts/shared types | Dùng chung PreparedDataset/Pattern |
| Eclat list/BitVector và rules | A đã merge; 622 checks A đạt khi review | Full suite A+B: 762 pass |
| Năm references SPMF | A/B chạy độc lập, cùng output hashes | Manifest chính giữ provenance B; logs hai bên giữ nguyên |
| Benchmark acquisition/harness | A đã triển khai; 35 cases/875 bản đo/70 maps | Giữ nguyên bằng chứng và phạm vi đo |
| Groceries preparation/export | B đã kiểm 9.835 baskets/169 items | Nối miner/rules, top-10 và diễn giải |
| Splice preparation/comparison | B giữ 3.185/3.190 mẫu, 48 IDs | Khai thác patterns thật theo lớp và diễn giải |
| Chương 1–2 | A có nguồn và PDF review | Cân trang báo cáo nhóm |
| Chương 3 | B có số liệu nguồn/tiền xử lý | Bổ sung kết quả khai thác thật |
| Notebook | Gộp setup B, miner/benchmark A | 7 cells local đạt; cần remote Colab cold-run |
| Report.pdf cuối và nghiệm thu M2/M3 | Chưa hoàn tất | Hai ứng dụng, Colab và báo cáo cuối |

Lịch sử kiểm chứng: docs/verification.md, docs/member-b-validation/ và
results/logs/. Không dùng candidates DNA thủ công trong test làm kết quả Eclat.
