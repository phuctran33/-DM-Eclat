# SPMF binary tham chiếu

```bash
python3 scripts/prepare_spmf.py --references
```

Script tải archive chính thức `https://www.philippe-fournier-viger.com/spmf/spmf2.64.jar`,
SPMF **2.64b**, pin SHA-256
`c67c2e56bdd2072eadc0e4bc96c8221cec38c9109f99c4b5f10be8eba64ec250`.
Cần Java ≥21 (class version 65); máy đo dùng Java 23.0.1. Bản latest không tương
thích Java 23 tại thời điểm chạy nên không được dùng để tạo số liệu.

File local là `tools/spmf.jar`, ignored và không commit. Nếu đã có JAR khác, script
reject hash thay vì ghi đè; lưu bản đó sang tên riêng rồi tải bản pin. Không copy
source Java thuật toán vào miner; binary chỉ dùng cho oracle/benchmark. Provenance
năm references nằm trong `tests/reference/spmf/manifest.csv`, logs trong
`results/reference/`. Không đồng nhất số version ECLAT in trong banner với version
SPMF distribution.
