# Hợp đồng dữ liệu v1.0.0

Đặc tả chính thức: [docs/SCHEMA.md](../docs/SCHEMA.md).
`contracts.toml` khóa field names, mapping, policies và CSV headers.

`tables/*.csv` chỉ có header để A/B viết exporter theo đúng schema; không chứa
kết quả thực nghiệm. `examples/groceries.csv` là dữ liệu minh họa tự tạo, không phải
dataset Groceries thực. `examples/dna_items.csv` là lookup đầy đủ 48 DNA tokens.

Nguồn, snapshot revision, SHA-256 và số đo phải lấy từ file/lần chạy thật.
