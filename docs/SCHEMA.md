# Dữ liệu và API Julia

Các cột CSV chuẩn khai báo trong [contracts.toml](../schemas/contracts.toml).
Mã kiểu và điều kiện hợp lệ nằm ở [structures.jl](../src/structures.jl) và
[schemas.jl](../src/schemas.jl). File xuất dùng UTF-8, CSV có header, counts
nguyên và support/confidence lưu dưới dạng tỷ lệ. Benchmark ghi `NA` cho chỉ
số chưa đo.

| API | Dữ liệu nhận và trả |
|---|---|
| `read_transactions(path)` | SPMF TXT sang `Vector{Vector{Int}}`, mỗi hàng có ID dương tăng dần |
| `parse_minsup(text)`, `minimum_count(relative, n)` | Decimal hoặc phần trăm sang rational, rồi ra `max(1, ceil(relative*n))` |
| `mine(transactions, min_count; backend=:list)` | `Vector{Pattern}`, toàn bộ itemset khác rỗng đủ ngưỡng. Backend thứ hai là `:bitset` |
| `write_patterns(path, patterns)`, `read_patterns(path)` | SPMF TXT dạng `1 2 #SUP: 3`, thứ tự xuất theo độ dài và tuple ID |
| `prepare_groceries(path)`, `prepare_splice(path)` | Trả `dataset`, `source_ids` và `audit`. Hai hàm `*_transactions` chỉ trả dataset |
| `association_rules(patterns, n; minconf=3//5)` | Tập phổ biến đầy đủ sang luật có counts, support, confidence và lift |
| `compare_dna_patterns(dataset, patterns_by_class)` | So support của ứng viên 2–4 item trên EI, IE và N |

`Pattern.items` là tuple ID tăng dần, `Pattern.support` là số giao dịch.
TID đếm từ một trong dữ liệu đã chuẩn hóa. Dòng trống, comment và metadata
SPMF bị bỏ. Hai giao dịch có cùng nội dung nhưng ở hai dòng vẫn có TID riêng.

`PreparedDataset` giữ `dataset_id`, `transactions`, mapping `item_labels`,
ID quan sát `row_ids` và `classes`. Chỉ `transactions` đi vào miner. Groceries
chuẩn hóa tên hàng NFC, chữ thường và khoảng trắng, gộp item trùng trong một
giỏ, sắp ID và giữ các giỏ riêng. Splice lấy cửa sổ 25:36, gán
`4*(slot-1)+base_index` với thứ tự A,C,G,T và giữ EI/IE/N ngoài giao dịch.
Biểu diễn 48 ID ổn định giữa các lớp. Record sai định dạng báo lỗi. Mẫu
Splice có ký hiệu mơ hồ trong cửa sổ được đếm trong audit rồi loại.

Luật xếp theo lift, confidence và support giảm dần, sau đó độ dài hợp hai vế
và ID tăng dần. Xét mọi cách chia mỗi tập frequent. Lọc confidence bằng tỉ
số count trước khi làm tròn. Bảng DNA hợp tập frequent từ các lớp, lọc độ dài
2–4 và đếm lại trên mọi lớp để lấy cả count dương dưới ngưỡng. Xếp theo
chênh lệch support giữa các lớp, support lớn nhất, độ dài và ID.

| Artifact | Ý nghĩa |
|---|---|
| `prepared/<dataset>/transactions.txt`, `items.csv` | Dòng SPMF đã chuẩn hóa, mapping ID và tên gốc đã chuẩn hóa |
| `prepared/<dataset>/observations.csv`, `preparation_audit.csv` | TID, mã nguồn, lớp và số quan sát giữ/loại |
| `groceries_rules.csv`, `groceries_top10.csv` | Luật đã xếp hạng, có nhãn, counts và chỉ số |
| `dna_patterns.csv` | Ứng viên, count và mẫu số mỗi lớp, support và độ chênh |
| `run.toml`, `validation.json` | Tham số, hash dữ liệu/mã/kết quả và đối chiếu Java SPMF |
| `tests/reference/spmf/manifest.csv` | Provenance của 5 toy ở 40% |
| `results/raw/benchmark_runs.csv` | Run ID, backend, scope, thời gian, RSS, count và trạng thái |

Các thư mục output mới giữ mẫu quan sát và numeric transactions để kiểm
chứng. Kết quả công bố giữ bảng, frequent itemsets, mapping và hash để có
thể sinh lại từ nguồn pin trong [manifest](../data/manifest.csv).
