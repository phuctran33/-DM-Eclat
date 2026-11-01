# Trạng thái trung thực của template

| Thành phần | Trạng thái | Bước tiếp theo |
|---|---|---|
| Schema A/B v1.0.0 và kiểu Julia | Đã chốt + validation tests | Triển khai theo docs/SCHEMA.md |
| Parser/writer SPMF, threshold, CLI | Đã có hạ tầng | Chạy lại test và tích hợp miner |
| Comparator `(itemset, support)` | Đã có, 5 oracle B khớp vét cạn | Chờ miner A được duyệt để đối chiếu |
| 5 toy DB và SPMF references B | Đã tạo thật, hashes/logs/test pass | Không lấy reference từ A |
| Eclat basic DFS | TODO | A triển khai M1 |
| Eclat BitVector | TODO | A triển khai sau gate M1 |
| Groceries preprocessing/export | Đã test trên 9.835 giỏ/169 item | Chờ A cho rule generation/mining |
| UCI Splice preprocessing/comparison | Đã test: 3.185 mẫu giữ, 5 loại | Chờ output mined từ A được duyệt |
| Worker timing / sinh subset và synthetic | Hạ tầng có sẵn | A thêm điều phối, RSS, aggregation và plots |
| SPMF references / benchmark thực | 5 references B đã chạy; benchmark chưa chạy trên main | Không dùng kết quả A chưa duyệt |
| Report.tex 3 chương và notebook | Template | Điền dữ liệu thực và cold-run |
| docs/Report.pdf / Colab cold-run | Chưa tạo / chưa chạy | Hoàn thiện M3 |
| GitHub repository | URL phuctran33/-DM-Eclat đã được nhóm cung cấp | Push template, kiểm quyền public trước nộp |

Không module nào được đánh dấu nghiệm thu chỉ vì thư mục hoặc TODO đã tồn tại.
Nhật ký xác minh template nằm tại `docs/verification.md`.

B: 206 test Julia, 4 Python pass; log trong docs/member-b-validation/.
