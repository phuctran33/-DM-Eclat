# Chess / Mushroom / Retail / T10I4D100K

```bash
python3 scripts/acquire_benchmarks.py
```

Nguồn FIMI học thuật gốc tại `https://www.cs.rpi.edu/~zaki/Workshops/FIMI/data/`;
URL/raw content hash/license notes trong `configs/datasets.toml`. Bản tải có gzip
magic dù URL là .dat. Giải nén và chuẩn hóa whitespace; Retail/T10 cộng 1 cho mọi
ID để chuyển ID 0 về ID dương. Không bỏ rows, không deduplicate các observations.
Ba backends nhận cùng normalized file. Script reject raw hash hoặc format khác.

Normalized SHA-256 và provenance trong `data/manifest.csv`,
`results/raw/dataset_provenance.json`; actual stats từ file ở
`results/raw/dataset_statistics.csv`. Chess n=3196/m=75; Mushroom 8124/119;
Retail 88162/16470; T10I4D100K 100000/870. Không thay bằng stats của snapshot khác.

Raw datasets không commit. Đây là content-addressed snapshot ở nguồn gốc, không
phải một version HF/Kaggle tự khai. FIMI không công bố license rõ cho mọi tập;
ghi đúng trạng thái đó, credit Tom Brijs/điều kiện sử dụng Retail từ trang nguồn.

Retail attribution: Brijs, Swinnen, Vanhoof và Wets (1999), *Using Association
Rules for Product Assortment Decisions: A Case Study*, KDD, pp. 254–260.
Điều kiện gốc: https://www.cs.rpi.edu/~zaki/Workshops/FIMI/data/retail.pdf.
Nhóm cần gửi bản nộp/final cho donor theo hướng dẫn tracking; không tự động gửi email.
