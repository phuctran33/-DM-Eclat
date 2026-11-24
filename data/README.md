# Dữ liệu và nguồn

<a id="benchmark"></a>
## Benchmark FIMI

Từ thư mục gốc, chạy `python3 scripts/acquire_benchmarks.py`. Script kiểm
SHA-256, giải nén gzip và chuẩn hóa khoảng trắng. Retail và T10I4D100K được
cộng 1 vào mọi item ID để giữ ID dương. Giữ nguyên số dòng và cho cả ba backend
đọc cùng file chuẩn hóa.

| Dữ liệu | Giao dịch | Items |
|---|---:|---:|
| Chess | 3.196 | 75 |
| Mushroom | 8.124 | 119 |
| Retail | 88.162 | 16.470 |
| T10I4D100K | 100.000 | 870 |

URL và hash thô nằm trong [cấu hình](../configs/datasets.toml). Hash chuẩn
hóa và thống kê thật nằm trong [provenance](../results/raw/dataset_provenance.json)
và [CSV](../results/raw/dataset_statistics.csv). Dữ liệu thô được tải tại chỗ
từ nguồn FIMI. FIMI chưa ghi rõ quyền tái phân phối cho Chess, Mushroom và
T10. [Kho FIMI](https://www.cs.rpi.edu/~zaki/Workshops/FIMI/data/)

Retail ghi nguồn Brijs, Swinnen, Vanhoof và Wets (KDD 1999, tr. 254–260).
Nhóm cần gửi bản nộp đầu và bản cuối cho bên cung cấp theo điều kiện
nguồn. [Điều kiện Retail](https://www.cs.rpi.edu/~zaki/Workshops/FIMI/data/retail.pdf)

<a id="ung-dung"></a>
## Hai ứng dụng

- Groceries dùng CSV snapshot Git có revision và SHA-256. Mỗi dòng là một
  giỏ, đổi thành các cặp `basket_id,item_name`. Snapshot được tải từ nguồn vì
  manifest chưa có điều khoản tái phân phối riêng. [arules Groceries](https://mhahsler.github.io/arules/reference/Groceries.html)
- Splice dùng `splice.data` có nhãn, mã quan sát và chuỗi 60 vị trí. Hai bản
  tải Szeged và ZIP UCI phải khớp cùng SHA-256. Nguồn UCI có giấy phép
  CC BY 4.0 và yêu cầu ghi nguồn. [UCI](https://doi.org/10.24432/C5M888)

Chạy `python3 scripts/prepare_application_data.py --dataset all`, hoặc chọn
`groceries` hay `splice`. Mỗi lượt lưu nguồn thực tế và kết quả chuẩn hóa.
[Manifest](manifest.csv) · [Schema Julia](../docs/SCHEMA.md)

<a id="toy-spmf"></a>
## Năm bộ toy và Java SPMF

| File trong `toy/` | Tình huống |
|---|---|
| `basic.txt` | Itemset nhiều độ dài và support bằng ngưỡng |
| `dense.txt` | Itemset dài trên dữ liệu dày |
| `sparse.txt` | ID không liên tiếp và output rỗng ở ngưỡng 40% |
| `duplicates.txt` | Hai giao dịch cùng nội dung vẫn có TID khác nhau |
| `boundary.txt` | Support đúng bằng ngưỡng được giữ |

Test kiểm năm bảng itemset/support tại 40%, oracle vét cạn ở nhiều ngưỡng
và các nguồn Java SPMF độc lập. Demo chạy lại Java SPMF và so cả itemset lẫn
support. Manifest giữ lệnh, phiên bản, hash nguồn, hash JAR và hash
reference. [Test miner](../tests/test_miner.jl) ·
[Manifest Java](../tests/reference/spmf/manifest.csv) ·
[Log tạo references](https://github.com/phuctran33/-DM-Eclat/tree/556602e66d79f90fa735100e4c58fd0ba59e6d91/docs/member-b-validation/spmf)
