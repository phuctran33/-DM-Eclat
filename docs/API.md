# API A/B — schema v1.0.0 đã chốt

Định nghĩa đầy đủ: [SCHEMA.md](SCHEMA.md). Kiểu dữ liệu ở `src/schemas.jl`.

| API | Input | Output / yêu cầu |
|---|---|---|
| `read_transactions(path)` | Numeric SPMF TXT | `Vector{Vector{Int}}`, dòng tăng dần, item dương và không trùng |
| `parse_minsup(text)` | `0.4`, `40%` | Rational chính xác trong `(0,1]` |
| `minimum_count(relative, n)` | Tỉ lệ, số giao dịch | `max(1, ceil(relative*n))` |
| `mine(transactions, min_count; backend=:list)` | Giao dịch chuẩn, absolute count ≥1 | `Vector{Pattern}`, mọi frequent itemset khác rỗng, đúng một lần |
| `mine(...; backend=:bitset)` | Cùng hợp đồng baseline | Kết quả giống tuyệt đối; thay biểu diễn tidset |
| `write_patterns(path, patterns)` | Pattern có key canonical | SPMF TXT, ổn định theo độ dài rồi itemset |
| `read_patterns(path)` | SPMF TXT numeric | `Dict{Itemset,Int}`, bỏ qua thứ tự dòng; phát hiện trùng |
| `association_rules(patterns, n; minconf=3//5)` | Output đầy đủ của miner | `Vector{AssociationRule}`, counts + support/confidence/lift, sort xác định |
| `groceries_transactions(path)` | Canonical CSV `basket_id,item_name` | `PreparedDataset`, classes=nothing |
| `splice_transactions(path; positions=25:36)` | UCI Splice raw, cửa sổ đã khóa | `PreparedDataset`, 48-ID mapping, metadata EI/IE/N |
| `compare_dna_patterns(dataset, patterns_by_class)` | PreparedDataset + Dict đủ EI/IE/N | `Vector{DNAPatternComparison}`, candidates 2–4 item |

`Pattern.items` là tuple ID tăng dần; `Pattern.support` là số giao dịch chứa itemset.
Support của itemset bằng đúng ngưỡng vẫn là frequent. Không đưa nhãn EI/IE/N vào
giao dịch mining; giữ riêng để so sánh theo lớp. Mã CLI parse support không qua Float64
để tránh `ceil(0.07*100)` lệch vì biểu diễn nhị phân.

Blank/comment/metadata input không tạo TID. Giữ các transaction giống nhau vì đây
là các quan sát độc lập. File input sai thứ tự/trùng item bị từ chối; helper chuẩn bị
dữ liệu phải chuẩn hóa rõ ràng, không âm thầm đổi dữ liệu trong parser.

`PreparedDataset` có `dataset_id,transactions,item_labels,row_ids,classes`.
A gọi `mine(prepared.transactions, min_count)`; B giữ mapping/metadata để diễn giải.
Stats/audit xuất riêng, không đổi return type. Preprocessing, miner và application
functions vẫn TODO; khai báo schema không thay cho việc triển khai.

M1 A/B đọc schema đã chốt và hoàn thiện pseudocode. M2 hai backend giữ cùng
ordering/candidate policy để so sánh tối ưu có ý nghĩa.
