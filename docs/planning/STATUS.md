# Trạng thái trung thực của template

| Thành phần | Trạng thái | Bước tiếp theo |
|---|---|---|
| Schema A/B v1.0.0 và kiểu Julia | Đã chốt + validation tests | Triển khai theo docs/SCHEMA.md |
| Parser/writer SPMF, threshold, CLI | Đã có hạ tầng | Chạy lại test và tích hợp miner |
| Comparator `(itemset, support)` | Đã có | B tạo reference bằng SPMF thật |
| 5 toy DB và expected độc lập | Đã chuẩn bị | B kiểm chứng với SPMF |
| Eclat basic DFS | TODO | A triển khai M1 |
| Eclat BitVector | TODO | A triển khai sau gate M1 |
| Groceries preprocessing/rules | TODO | B chủ trì; A hỗ trợ rules |
| UCI Splice DNA | Schema đã khóa; helper TODO | B triển khai window 25:36, mapping 48 ID, drop ambiguous window |
| Worker timing / sinh subset và synthetic | Hạ tầng có sẵn | A thêm điều phối, RSS, aggregation và plots |
| SPMF references / benchmark thực | Chưa chạy | Không có tỉ lệ đúng hay speedup để công bố |
| Report.tex 3 chương và notebook | Template | Điền dữ liệu thực và cold-run |
| docs/Report.pdf / Colab cold-run | Chưa tạo / chưa chạy | Hoàn thiện M3 |
| GitHub repository | URL phuctran33/-DM-Eclat đã được nhóm cung cấp | Push template, kiểm quyền public trước nộp |

Không module nào được đánh dấu nghiệm thu chỉ vì thư mục hoặc TODO đã tồn tại.
Nhật ký xác minh template nằm tại `docs/verification.md`.
