# Dữ liệu và nguồn

<a id="benchmark"></a>
## Benchmark FIMI

Từ gốc repo, chạy `python3 scripts/acquire_benchmarks.py`. Có thể thêm
`--report .tools/acquisition/sources.json` để lưu JSON vào đường dẫn mới.
Demo tự lưu JSON trong thư mục `OUTPUT`. Script thử cache đã kiểm hash trước,
rồi thử các URL công khai theo thứ tự trong cấu hình. `--offline` chỉ đọc cache.
[Cấu hình tải hiện hành](../configs/datasets.toml)

| Dữ liệu | Giao dịch | Items | Ưu tiên · FIMI RPI | Dự phòng · FIMI Antwerp | Dự phòng · SPMF |
|---|---:|---:|---|---|---|
| Chess | 3.196 | 75 | [gzip](https://www.cs.rpi.edu/~zaki/Workshops/FIMI/data/chess.dat) | [text](https://fimi.uantwerpen.be/data/chess.dat) | [text](https://www.philippe-fournier-viger.com/spmf/publicdatasets/chess.txt) |
| Mushroom | 8.124 | 119 | [gzip](https://www.cs.rpi.edu/~zaki/Workshops/FIMI/data/mushroom.dat) | [text](https://fimi.uantwerpen.be/data/mushroom.dat) | — |
| Retail | 88.162 | 16.470 | [gzip](https://www.cs.rpi.edu/~zaki/Workshops/FIMI/data/retail.dat) | [text](https://fimi.uantwerpen.be/data/retail.dat) | [text](https://www.philippe-fournier-viger.com/spmf/publicdatasets/retail.txt) |
| T10I4D100K | 100.000 | 870 | [gzip](https://www.cs.rpi.edu/~zaki/Workshops/FIMI/data/T10I4D100K.dat) | [text](https://fimi.uantwerpen.be/data/T10I4D100K.dat) | [text](https://www.philippe-fournier-viger.com/spmf/publicdatasets/T10I4D100K.txt) |

Script giải gzip theo magic bytes, chuẩn hóa khoảng trắng và giữ nguyên thứ tự
giao dịch. Hai kho FIMI cần offset `+1` cho Retail và T10I4D100K. Bản SPMF của
hai bộ này dùng ID dương sẵn, nên offset `0`. Chess và Mushroom dùng offset
`0`. URL Mushroom trong danh mục SPMF trả 8.416 hàng nên bị loại khi kiểm nguồn.
[Danh mục SPMF](https://www.philippe-fournier-viger.com/spmf/index.php?link=datasets.php)

Khi kiểm các URL trong bảng, thứ tự giao dịch, tần suất từng item và phân bố
độ rộng đều trùng bản đo. SHA-256 sau chuẩn hóa giống nhau theo từng bộ:

| Dữ liệu | SHA-256 sau chuẩn hóa |
|---|---|
| Chess | `341d0ff8676e053dd3b417d61f84c732736154f987ce56975a099b07460957f5` |
| Mushroom | `06206c73983251a9488414c4379a030e836bbeb6fe9eff1b5624a0193a811640` |
| Retail | `417563fb5feb3711d4f761230ca78b76d100fe2ee0d3178fcc4fbb000d8d1c36` |
| T10I4D100K | `fb2dd118ff822ff88d724e47d5a4cea6531c0bd6294397db4d36890c1450f1a7` |

Cache nạp vào `.tools/acquisition/`, input chuẩn hóa vào `data/benchmark/`.
Nếu một bộ hết nguồn hợp lệ, script báo lỗi trước khi ghi input chuẩn hóa.
Manifest, provenance và CSV thống kê lưu lần đo công bố. JSON của phiên tải
ghi URL thực tế, hash thô và hash chuẩn hóa riêng. [Manifest](manifest.csv) ·
[Provenance gốc](../results/raw/dataset_provenance.json) · [Thống kê gốc](../results/raw/dataset_statistics.csv)

Chess và Mushroom là biến thể UCI do Roberto Bayardo chuẩn bị. T10I4D100K
là dữ liệu tổng hợp IBM Quest. Kho FIMI chưa nêu quyền tái phân phối cụ thể
cho ba snapshot này. Repo chỉ lưu liên kết để tải trực tiếp. [Kho FIMI](https://fimi.uantwerpen.be/data/)

Retail ghi nguồn Brijs, Swinnen, Vanhoof và Wets (KDD 1999, tr. 254–260).
Điều kiện sử dụng yêu cầu gửi bản nộp đầu và bản cuối kèm tên và ngày công bố
cho bên cung cấp. Đồ án nhóm ghi tên môn và ngày nộp thực tế khi xác nhận với bên
cung cấp. [Điều kiện Retail](https://www.cs.rpi.edu/~zaki/Workshops/FIMI/data/retail.pdf)

<a id="ung-dung"></a>
## Hai ứng dụng

- Groceries dùng CSV snapshot Git có revision và SHA-256. Mỗi dòng là một
  giỏ, đổi thành các cặp `basket_id,item_name`. Snapshot được tải từ nguồn vì
  manifest chưa có điều khoản tái phân phối riêng. [arules Groceries](https://mhahsler.github.io/arules/reference/Groceries.html)
- Splice dùng `splice.data` có nhãn, mã quan sát và chuỗi 60 vị trí. Hai bản
  tải Szeged và ZIP UCI phải khớp cùng SHA-256. Nguồn UCI có giấy phép
  CC BY 4.0 và yêu cầu ghi nguồn. [UCI](https://doi.org/10.24432/C5M888)

Chạy `python3 scripts/prepare_application_data.py --dataset all`, hoặc chọn
`groceries` hay `splice`. Mỗi lượt lưu nguồn thực tế trong
`data/applications/*_source.json` và notebook lưu một bản trong `OUTPUT`.
[Manifest lịch sử](manifest.csv) · [Schema Julia](../docs/SCHEMA.md)

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
