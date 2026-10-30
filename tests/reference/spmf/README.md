# Kết quả tham chiếu thực sự từ SPMF

Chưa có kết quả SPMF trong template. Tạo 5 file `basic.txt`, `dense.txt`,
`sparse.txt`, `duplicates.txt`, `boundary.txt` bằng Eclat của SPMF, minsup **40%**.
Ví dụ chạy từ repo root, sau khi có Java và `tools/spmf.jar`:

```text
java -jar tools/spmf.jar run Eclat data/toy/basic.txt tests/reference/spmf/basic.txt 40%
```

Lặp lại cho 4 tên còn lại. Lưu phiên bản Java/SPMF, SHA-256 của JAR và input,
lệnh thực tế và stdout vào `results/reference/`. Không sửa tay các support để test pass.

Bật `ECLAT_TEST_MINER=1` và `ECLAT_TEST_SPMF=1` (M1 mặc định kiểm backend `list`;
M2/final thêm `ECLAT_TEST_BACKENDS=list,bitset`), sau đó chạy
`julia --project=. tests/runtests.jl`. Test SPMF sẽ fail nếu thiếu file.
Không bật tùy chọn giới hạn độ dài itemset khi tạo kết quả tham chiếu.
