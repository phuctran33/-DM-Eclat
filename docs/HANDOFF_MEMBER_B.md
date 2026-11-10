> M2 10/11/2026: pipeline mined thật đã triển khai. Xem [M2_MEMBER_B.md](M2_MEMBER_B.md) cho trạng thái hiện tại; phần dưới giữ nguyên lịch sử bàn giao trước M2.

> Cập nhật 05/11/2026: A đã merge vào main qua PR #1 (`b821235`). Nhánh B
> cập nhật main để xử lý conflict PR #3, giữ cả code A và B. Các câu chờ A bên
> dưới mô tả lịch sử lần bàn giao 01/11; pipeline ứng dụng mined cuối vẫn cần
> hoàn thiện. Kiểm chứng sau tích hợp: member-b-validation/integration-main.log.

# Bàn giao B — nhánh độc lập từ main

Ngày kiểm chứng: **01/11/2026**. Nhánh: **feat/member-b-applications**.
Base: **e1c986574305670af883da260a0a534761ecbc73**, origin/main.
Không merge/cherry-pick/copy implementation từ nhánh A chưa duyệt. Miner/rules và
schema dùng chung giữ nguyên nội dung đã duyệt trên main.

## Kết quả đã chạy thật

| Kiểm chứng | Kết quả |
|---|---|
| Julia suite riêng B | **206 pass, 0 fail/error/skip** |
| Python acquisition/adapter regressions | **4 pass** |
| Groceries thật | 9.835 giỏ, 169 item, 43.367 dòng canonical long CSV |
| Splice thật | 3.190 mẫu raw, giữ 3.185; 48 position/base IDs |
| EI | Giữ 765, loại 2 vì ambiguous window |
| IE | Giữ 766, loại 2 |
| N | Giữ 1.654, loại 1 |
| Oracle SPMF | 5 reference thật ở 40%, khớp vét cạn toàn bộ map |
| Real-data integration | Mọi transaction/mapping/metadata/audit khớp oracle Python |
| Tính tái lập | Hai lần export giống từng byte; từ chối ghi đè giữ nguyên dữ liệu |
| Source isolation | Suite B + tái tạo toàn bộ dữ liệu pass trong bản sao source sạch |
| Notebook local | Tất cả 7 code cells chạy thật; miner/apps mining tắt |

Log và báo cáo thực tế trong [member-b-validation/](member-b-validation/).
Hai candidates DNA chọn thủ công chỉ để kiểm tra routine so sánh bằng dữ liệu thật,
không được gọi là output Eclat hoặc kết quả ứng dụng cuối.

## Code B

- src/applications/io.jl: CSV nghiêm ngặt, quoted comma/newline/quote, BOM/CRLF,
  UTF-8 và output transactions/items/observations/audit vào thư mục mới/rỗng.
- groceries.jl: NFC/lowercase/whitespace, mapping ổn định, giữ basket khác ID,
  audit duplicate item rows; trả đúng PreparedDataset.
- dna.jl: window 25:36, 48 IDs, metadata EI/IE/N, kiểm IUPAC/độ dài, loại ambiguity
  trong window; so sánh pattern caller cung cấp bằng cách đếm lại mọi lớp.
- export_rules.jl: xuất/sort/top-k luật caller cung cấp, không tự sinh luật hoặc mine.
- scripts/prepare_application_data.py: tải/kiểm source hash và adapter canonical;
  Python chỉ dùng stdlib, không có thư viện FIM.
- scripts/prepare_applications.jl, compare_dna.jl: CLI độc lập của B.
- scripts/prepare_references_b.py: tự chạy JAR SPMF chính thức, đối chiếu vét cạn,
  lưu reference/manifest và nguyên stdout/stderr; không lấy artifacts A.

Kiểm thử gồm unit/edge cases, source checksum/offline/failure cases, Unicode thật,
metadata sai, support khai báo sai, CLI chạy process thật và dữ liệu đầy đủ.

## Nguồn và runtime

Julia portable **1.10.10** tại `.tools/julia-1.10.10/bin/julia.exe`, ZIP đã kiểm
checksum chính thức. Chỉ dùng Base/stdlib, thêm Unicode stdlib. Không đổi PATH hệ thống.
Java mặc định của máy là Java 8; tái tạo SPMF dùng **Java 21.0.9 có sẵn trong CLion**,
truyền --java, không đổi Java mặc định. JAR SPMF **2.64b** từ archive chính thức,
SHA-256 c67c2e56bdd2072eadc0e4bc96c8221cec38c9109f99c4b5f10be8eba64ec250.

Groceries: CSV mirror stedy/Machine-Learning-with-R-datasets, commit
`d20658ec6d336af2d4ddb5fd72b6f677dd46136e`, raw SHA-256
`ff1be892fd6b9b57d1a7bc50de067798963dda607619645988b21789bf23ae3b`.
Nguồn gốc dataset được mô tả bởi arules/Hahsler; không gọi CSV mirror là endpoint gốc.

Splice: raw UCI được lưu tại kho học thuật Đại học Szeged; endpoint UCI chính thức
đã timeout nên dùng mirror **ghi rõ trong provenance**, pin raw SHA-256
`ebbae10c85d3c285e2a2489a37e42bc2ee8d91d15005e391a9962fa3389a114f`.
Giữ source IDs, thứ tự và toàn bộ raw records, không dùng bản đã bỏ mẫu/one-hot.
Nguồn gốc và giấy phép: UCI DOI 10.24432/C5M888, CC BY 4.0.
Raw/prepared data và runtime/JAR được ignore; chỉ lưu log/hash/thống kê nhỏ.

## Lệnh tái lập

Từ repo root, dùng julia trong PATH hoặc đường dẫn portable tương ứng:

```text
julia --project=. tests/runtests_b.jl
python -B tests/test_application_sources.py
python scripts/prepare_application_data.py --dataset all
julia --project=. scripts/prepare_applications.jl groceries data/applications/groceries.csv data/applications/processed/groceries
julia --project=. scripts/prepare_applications.jl splice data/applications/splice.data data/applications/processed/splice
python -B tests/verify_prepared_data.py --julia PATH_TO_JULIA --report docs/member-b-validation/preparation-report.json
python scripts/prepare_references_b.py --java PATH_TO_JAVA_21
```

Output directory phải mới/rỗng. Có cache source đúng checksum thì thêm --offline
cho scripts nguồn/reference. Không dùng --offline khi chưa tải JAR/source.

## Phần chờ A được duyệt

Basic/BitVector/rule generation trên main vẫn TODO. Sau khi A merge, B nối miner
với PreparedDataset để có top-10 luật Groceries, pattern DNA mined thật, diễn giải
và hoàn thiện Chương 3/Colab. Không dùng fixture hoặc candidates thủ công thay kết
quả ứng dụng. Suite project chung còn hai pending markers cho mining/SPMF-miner;
suite B độc lập không có skip. Chưa tuyên bố M1/M2/M3 toàn nhóm đã nghiệm thu.

Các thay đổi được cô lập trên nhánh B; dùng git log -1 để xác định commit bàn giao.
Không push/merge main hoặc sửa nhánh A. Remote CI/Colab chưa được chạy.
