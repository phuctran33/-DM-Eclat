# API và hợp đồng dữ liệu — gói 01 / M1

| API | Input | Output / yêu cầu |
|---|---|---|
| `read_transactions(path)` | Numeric SPMF TXT | `Vector{Vector{Int}}`, dòng tăng dần, item dương và không trùng |
| `parse_minsup(text)` | `0.4`, `40%` | Rational chính xác trong `(0,1]` |
| `minimum_count(relative, n)` | Tỉ lệ, số giao dịch | `max(1, ceil(relative*n))` |
| `mine(transactions, min_count; backend=:list)` | Giao dịch chuẩn, absolute count ≥1 | `Vector{Pattern}`, mọi frequent itemset khác rỗng, đúng một lần |
| `mine(...; backend=:bitset)` | Cùng hợp đồng baseline | Kết quả giống tuyệt đối; thay biểu diễn tidset |
| `write_patterns(path, patterns)` | Pattern có key canonical | SPMF TXT, ổn định theo độ dài rồi itemset |
| `read_patterns(path)` | SPMF TXT numeric | `Dict{Itemset,Int}`, bỏ qua thứ tự dòng; phát hiện trùng |
| `association_rules(patterns, n; minconf=0.6)` | Output đầy đủ của miner | TODO A hỗ trợ B: schema rules có support/count/confidence/lift |
| `groceries_transactions(path)` | Raw Groceries đã chốt schema | TODO B: transactions + mapping tên + thống kê |
| `splice_transactions(path; positions=25:36)` | UCI Splice raw | TODO B: transactions + labels + IDs + mapping + thống kê |
| `compare_dna_patterns(transactions, labels, patterns)` | Output nhóm và dữ liệu theo lớp | TODO B: bảng support EI/IE/N cho pattern 2–4 item |

`Pattern.items` là tuple ID tăng dần; `Pattern.support` là số giao dịch chứa itemset.
Support của itemset bằng đúng ngưỡng vẫn là frequent. Không đưa nhãn EI/IE/N vào
giao dịch mining; giữ riêng để so sánh theo lớp. Mã CLI parse support không qua Float64
để tránh `ceil(0.07*100)` lệch vì biểu diễn nhị phân.

Blank/comment/metadata input không tạo TID. Giữ các transaction giống nhau vì đây
là các quan sát độc lập. File input sai thứ tự/trùng item bị từ chối; helper chuẩn bị
dữ liệu phải chuẩn hóa rõ ràng, không âm thầm đổi dữ liệu trong parser.

M1: A/B chốt pseudocode và schema ứng dụng cụ thể trước khi triển khai TODO. M2:
hai backend phải dùng cùng ordering/candidate policy để so sánh tối ưu có ý nghĩa.
