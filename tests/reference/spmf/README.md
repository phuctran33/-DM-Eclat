# Năm reference SPMF thật

`basic.txt`, `dense.txt`, `sparse.txt`, `duplicates.txt`, `boundary.txt` được tạo
bằng **SPMF 2.64b Eclat**, Java 23.0.1, tại minsup 40%, không giới hạn pattern length.
Không viết tay hay lấy expected của brute-force để gọi là SPMF. Sparse có output
rỗng hợp lệ ở count 3; bốn fixture còn lại lần lượt có 7/14/5/4 patterns.

```bash
python3 scripts/prepare_spmf.py --references
julia --project=. tests/runtests.jl
```

Script kiểm JAR pin chính thức trước khi chạy Java và lưu stdout/stderr/command.
Manifest giữ đúng header schema v1.0.0 với input/output/JAR SHA-256, versions,
threshold, count và command. `tests/test_benchmark.py` kiểm hashes reference;
Julia test so toàn bộ canonical itemset/support map ở cả list và bitset.
Không cần JAR để đọc các references đã pin trong unit tests; cần Java/JAR để tự
regenerate hoặc chạy integration smoke/benchmark.
