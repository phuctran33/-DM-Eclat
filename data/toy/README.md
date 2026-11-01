# Năm CSDL nhỏ cho M1

| File | Tình huống |
|---|---|
| basic.txt | Pattern chung, support boundary, nhiều độ dài |
| dense.txt | Nhiều item cùng xuất hiện, có itemset dài |
| sparse.txt | Ít đồng xuất hiện, ID không liên tiếp |
| duplicates.txt | Các transaction giống nhau vẫn có TID khác nhau |
| boundary.txt | Support đúng bằng ngưỡng phải được giữ |

Các file `*.expected.txt` được liệt kê bằng exhaustive subset counting độc lập,
ở **minsup 40%**; chúng không phải output chạy SPMF. Test miner còn dùng oracle
brute-force ở nhiều ngưỡng và dữ liệu ngẫu nhiên. References SPMF thật đã được tạo trong `tests/reference/spmf/`, pin bằng manifest;
full tests so toàn bộ `(itemset, support)` cho cả hai backends.
Không đọc các file expected như transaction database.
