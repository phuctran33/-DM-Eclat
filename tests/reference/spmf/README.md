# Kết quả tham chiếu thực sự từ SPMF

Nhánh B đã tự tạo và kiểm chứng 5 file `basic.txt`, `dense.txt`,
`sparse.txt`, `duplicates.txt`, `boundary.txt` bằng Eclat của SPMF, minsup **40%**.
Ví dụ chạy từ repo root, sau khi có Java và `tools/spmf.jar`:

```text
java -jar tools/spmf.jar run Eclat data/toy/basic.txt tests/reference/spmf/basic.txt 40%
```

Lặp lại cho 4 tên còn lại. Lưu phiên bản Java/SPMF, SHA-256 của JAR và input,
lệnh thực tế và stdout vào `results/reference/`. Không sửa tay các support để test pass.

Sau khi miner A được duyệt/merge, bật `ECLAT_TEST_MINER=1` và `ECLAT_TEST_SPMF=1` (M1 mặc định kiểm backend `list`;
M2/final thêm `ECLAT_TEST_BACKENDS=list,bitset`), sau đó chạy
`julia --project=. tests/runtests.jl`. Test SPMF sẽ fail nếu thiếu file.
Không bật tùy chọn giới hạn độ dài itemset khi tạo kết quả tham chiếu.


Tái tạo riêng B: python scripts/prepare_references_b.py --java PATH_TO_JAVA_21.
SPMF 2.64b pin checksum, five outputs khớp vét cạn tại 40%. Log thực tế nằm trong
docs/member-b-validation/spmf/. Test metadata/reference riêng không gọi miner:
julia --project=. tests/runtests_b.jl. Điều này chưa xác nhận miner main đã đúng.


Reference được chuẩn hóa CRLF→LF sau khi so map với oracle, để Git checkout trên
Windows/Linux giữ đúng checksum. Không đổi itemset/support hoặc thứ tự dòng.
Summary lưu cả raw_output_sha256 và output_sha256 canonical để truy vết.
