# Frequent Itemset Mining — ECLAT / Julia

Phần Member A — **Nguyễn Đức Hưng**: ECLAT Basic, BitVector, association-rule helper,
correctness, benchmark harness và Chương 1–2 đã triển khai. Hai backend xuất mọi
frequent itemset cùng support tuyệt đối, giữ nguyên **schema A/B v1.0.0**.
Bằng chứng đo, test và giới hạn tại [verification](docs/verification.md),
[experiments](docs/experiments.md) và [handoff](docs/HANDOFF_MEMBER_A.md).

Phần Member B — **Trần Thiên Phúc**: Groceries/DNA preprocessing, ứng dụng thực tế,
Colab cold-run và Chương 3 vẫn pending; không xem miner pass là hoàn thành các phần đó.
[Report nguồn](docs/latex/Report.tex) giữ đủ cấu trúc ba chương.
[PDF review phần A](docs/Member-A-review.pdf) là tài liệu kiểm tra Chương 1–2,
chưa thay thế `docs/Report.pdf` cuối của nhóm.

Dựa trên [đề HCMUS](https://hcmus-cs-ta.github.io/lab-book/data-mining/projects/itemset/)
và M. J. Zaki, *Scalable Algorithms for Association Mining*, IEEE TKDE 12(3),
372–390, 2000, [DOI](https://doi.org/10.1109/69.846291).
[Paper notes](docs/paper-notes.md) giải thích DFS prefix extension adaptation;
không gọi DFS của nhóm là bản chép Fig.12 bottom-up trong paper.

## Cài đặt và chạy miner

Cần [Julia ≥1.9](https://julialang.org/downloads/). Core chỉ dùng Base/stdlib;
`Manifest.toml` được tạo bằng Julia 1.10.10. Chạy từ repo root:

```bash
julia --project=. -e 'using Pkg; Pkg.instantiate()'
julia --project=. scripts/mine.jl --input data/toy/basic.txt --output results/basic.txt --minsup 0.4 --backend list
julia --project=. scripts/mine.jl --input data/toy/basic.txt --output results/bitset.txt --min-count 2 --backend bitset
```

Fixture này có 5 transactions, count=2 và 7 patterns. Input mỗi dòng là transaction
ID dương tăng dần, không trùng item. Giữ các rows giống nhau; reject item invalid,
không sort/sửa ngầm. Output dạng `1 2 #SUP: 3`, sort theo length rồi tuple.
Minsup parse chính xác từ decimal/percent; `0.07 × 100` cho count 7.
Xem [API](docs/API.md), [schema](docs/SCHEMA.md), [contracts](schemas/contracts.toml).

```julia
using EclatProject
transactions = [[1, 2], [1], [2]]
patterns = mine(transactions, 1; backend=:bitset) # Vector{Pattern}
rules = association_rules(patterns, 3; minconf=1//2)
```

Rules gồm mọi antecedent/consequent hợp lệ, consequent có thể nhiều item; support
của subset thiếu là lỗi. Helper giữ ranking và counts theo schema, không phụ thuộc
mappings Groceries/DNA chưa hoàn tất của B.

## Correctness và SPMF

Cần Java ≥21 và Python ≥3.11 để tạo lại reference/chạy controller. Pin SPMF **2.64b**
từ [archive chính thức](https://www.philippe-fournier-viger.com/spmf/index.php?link=download.php),
JAR SHA-256 được kiểm bởi script; không commit JAR hoặc sao chép source thuật toán.

```bash
python3 scripts/prepare_spmf.py --references
julia --project=. tests/runtests.jl
python3 tests/test_benchmark.py -v
python3 tests/smoke_benchmark.py
julia --project=. scripts/compare_spmf.jl results/basic.txt tests/reference/spmf/basic.txt
```

Mining tests mặc định bật `list,bitset` và năm references thật. Có exhaustive oracle,
randomized tests, empty/invalid/duplicate cases, packed-word tails, caller ownership,
rules/PreparedDataset và CLI. Để ghi rõ cấu hình final:

```bash
ECLAT_TEST_MINER=1 ECLAT_TEST_SPMF=1 ECLAT_TEST_BACKENDS=list,bitset julia --project=. tests/runtests.jl
```

**622 Julia checks pass, 0 fail/error/skip**; controller 5/5 tests pass. Stdout thật
của lần kiểm thử cuối và tổng pass/fail/skip nằm trong
[final-tests.log](results/logs/final-tests.log). References/hash provenance ở
[manifest](tests/reference/spmf/manifest.csv); output tự tính của toy fixtures không
được gọi là reference SPMF.

## Dữ liệu và thực nghiệm

Bốn benchmark: Chess, Mushroom, Retail, T10I4D100K. Acquisition từ
[FIMI học thuật](https://www.cs.rpi.edu/~zaki/Workshops/FIMI/data/), pin raw SHA-256
trong [datasets.toml](configs/datasets.toml), giữ normalized hashes trong
[manifest](data/manifest.csv). Retail/T10 có ID 0: cộng 1 cho **toàn bộ** IDs, không
bỏ giao dịch. Ba backends nhận cùng normalized file. Đây là content-addressed FIMI
snapshot; không gắn nhãn một HF/Kaggle revision chưa xác minh. Raw data bị ignore.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-plot.txt
python scripts/acquire_benchmarks.py
julia --project=. scripts/benchmark_runner.jl --phase pilot --repeats 1 --output results/new-pilot
JULIA_NUM_THREADS=1 julia --project=. scripts/benchmark_runner.jl --output results/reproduced
python scripts/plot_results.py --results results/reproduced --report
```

Grid sáu minsup/tập × ba backends × năm repetitions; thêm Retail nested
10/25/50/75/100% và synthetic widths 5/10/15/20/25/30 (seed 42). Timeout, exit status,
stdout/stderr, hashes và full-map equality được lưu thật. Peak RSS lấy từ OS;
allocation không phải peak memory. Có hai scope riêng:

| Scope | So sánh |
|---|---|
| end_to_end | Basic/BitVector/SPMF, gồm startup/JIT/JVM, read/mine/write |
| internal_read_mine | Hai backend Julia sau warm-up đầy đủ case; không so trực tiếp SPMF |

[Raw runs](results/raw/benchmark_runs.csv), [summary](results/raw/summary.csv),
[correctness](results/correctness/comparisons.csv), [figures](results/plots/),
[dataset statistics](results/raw/dataset_statistics.csv),
[environment](results/raw/environment.json) và [protocol](results/raw/protocol.json).
Số liệu không phải cam kết hiệu năng trên máy khác; xem giới hạn và cách resume
trong [experiments](docs/experiments.md). Logs process được giữ trong archive:

```bash
tar -xzf results/logs/benchmark-logs.tar.gz -C results/logs
```

## Báo cáo và bàn giao

```bash
cd docs/latex
latexmk -pdf -interaction=nonstopmode -halt-on-error MemberAReview.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error Report.tex
```

Cần IEEEtran, vntex, babel-vietnamese, algorithm/algpseudocode trong TeX Live.
`MemberAReview.tex` chỉ đưa Chương 1–2; `Report.tex` vẫn gồm Chương 3 của B với trạng
thái pending được ghi rõ. Các hình/bảng được tạo từ CSV, có caption/label/reference;
PDF cuối 10–15 trang và `docs/Report.pdf` cần B hoàn thiện ứng dụng/Chương 3 rồi cả
nhóm rà soát, không tự đánh dấu xong.

[Colab template](https://colab.research.google.com/github/phuctran33/-DM-Eclat/blob/main/notebooks/demo.ipynb)
chưa cold-run. Notebook của B còn cờ/tế bào template; để dùng miner ngay, import
API hoặc CLI ở trên. [Status](docs/planning/STATUS.md) phân biệt phần đã chạy với
việc còn lại. Các mốc module trong kế hoạch là lịch nội bộ, không suy ra hạn Moodle.

## Stdout kiểm thử cuối (31/10/2026)

```text
Test Summary:                     | Pass  Total  Time
SPMF I/O and canonical comparison |   14     14  2.3s
Test Summary:                           | Pass  Total  Time
Threshold boundaries and API validation |   19     19  0.0s
Test Summary:    | Pass  Total  Time
Shared schema v1 |   33     33  2.1s
Test Summary:                                          | Pass  Total  Time
Edge cases, input ownership and packed-word boundaries |  267    267  2.9s
Test Summary:                                      | Pass  Total  Time
Eclat: five different databases, selected backends |   80     80  0.1s
Test Summary:                                      | Pass  Total  Time
Randomized oracle and transaction-order invariance |   80     80  0.6s
Test Summary:                                     | Pass  Total  Time
Association rules and PreparedDataset integration |   94     94  4.0s
Test Summary:                    | Pass  Total   Time
CLI round trip and failure paths |   10     10  12.5s
Test Summary:                               | Pass  Total  Time
Exact agreement with SPMF on five databases |   25     25  0.1s
```
