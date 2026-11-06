# Năm references SPMF thật

SPMF 2.64b, minsup 40%, JAR SHA-256
`c67c2e56bdd2072eadc0e4bc96c8221cec38c9109f99c4b5f10be8eba64ec250`.

A và B đã chạy Java độc lập, có cùng canonical output hashes: basic 7, dense 14,
sparse 0, duplicates 5, boundary 4. Manifest chính giữ command/Java version của
lần chạy B; logs B tại docs/member-b-validation/spmf/, logs A tại results/reference/.
Không trộn version/command hai lần chạy hoặc thay references bằng expected tự đếm.

Tái tạo B (Java >=21, Windows/Linux/macOS):

```text
python scripts/prepare_references_b.py --java PATH_TO_JAVA_21
```

Tái tạo A (Linux/macOS vì dùng process monitor POSIX):

```bash
python scripts/prepare_spmf.py --references
```

References canonical LF, không đổi itemset/support/thứ tự; summary B giữ cả
raw_output_sha256 và output_sha256. Manifest đúng header schema v1.0.0.
Unit tests không cần Java/JAR; tái tạo cần binary chính thức. Kiểm metadata/hash
và vét cạn bằng tests/runtests_b.jl; full suite tests/runtests.jl còn so toàn bộ map
của miner list/bitset với references.
