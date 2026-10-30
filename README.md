# Đồ án Frequent Itemset Mining — Eclat / Julia

> **Trạng thái: project template.** Hạ tầng I/O, CLI, comparator và dữ liệu toy có sẵn.
> Eclat basic, BitVector, Groceries, DNA và bộ điều phối benchmark còn TODO.
> Chưa có kết quả SPMF, benchmark hoặc kết luận ứng dụng. Xem [tiến độ](docs/planning/STATUS.md).

**Schema A/B v1.0.0 đã chốt:** [đặc tả đầy đủ](docs/SCHEMA.md),
[hợp đồng dạng TOML](schemas/contracts.toml), shared types trong `src/schemas.jl`.
Preprocessing trả `PreparedDataset`; DNA cố định 25:36/48 item IDs;
Groceries nhận CSV `basket_id,item_name`. A/B triển khai theo cùng hợp đồng này.

Template bám [đề HCMUS](https://hcmus-cs-ta.github.io/lab-book/data-mining/projects/itemset/),
paper **Mohammed J. Zaki, “Scalable Algorithms for Association Mining”, IEEE TKDE,
12(3), 372–390, 2000**, [DOI](https://doi.org/10.1109/69.846291), và kế hoạch nhóm
`Ke_hoach_Eclat_Julia_3_tuan_theo_module.pdf` do nhóm cung cấp.

## Thành viên và lịch nội bộ

| Vai trò | Họ tên / MSSV | Chủ trì | Review |
|---|---|---|---|
| A | Nguyễn Đức Hưng | Eclat, tối ưu, benchmark, Chương 1–2 | Test, ứng dụng, bàn giao |
| B | Trần Thiên Phúc | SPMF/test, Groceries, Splice DNA, Colab, Chương 3 | Thuật toán và số liệu |

| Module | Thời gian năm 2026 | Mốc nghiệm thu | Kết quả cần đạt |
|---|---|---|---|
| M1 — Foundation + Correctness | 28/10–03/11 | 03/11 | Basic + CLI, khớp SPMF 100% trên ≥5 toy DB |
| M2 — Optimization + Applications | 04/11–10/11 | 10/11 | BitVector đúng; Groceries và DNA chạy được; Colab tối thiểu |
| M3 — Evaluation + Delivery | 11/11–17/11 | 17/11 | 4 benchmark, biểu đồ, Report.pdf, Colab và GitHub công khai |

Đây là **lịch nội bộ**, chưa phải deadline Moodle. Chỉ sync 20–30 phút ở mốc
nghiệm thu; không bắt buộc commit, PR hoặc báo cáo hằng ngày. Ngày 16–17/11 dành
cho cold-run và sửa lỗi. Chi tiết: [kế hoạch 3 module / 9 gói việc](docs/planning/PLAN.md).

## Cài đặt

Cài [Julia](https://julialang.org/downloads/) **1.9+**. Mã template chỉ dùng
Julia Base/stdlib. Chạy mọi lệnh từ repo root:

```text
julia --project=. -e "using Pkg; Pkg.instantiate()"
julia --project=. tests/runtests.jl
julia --project=. scripts/mine.jl --help
```

Lần đầu chạy Julia có thể có chi phí biên dịch JIT. Cần Java để chạy SPMF tham chiếu;
tự tải `spmf.jar` từ [SPMF](https://www.philippe-fournier-viger.com/spmf/), đặt tại
`tools/spmf.jar`. Không đưa mã Java SPMF vào phần cài đặt Eclat của nhóm.

## Cách chạy sau khi hoàn thành M1/M2

```text
julia --project=. scripts/mine.jl --input data/toy/basic.txt --output results/basic.txt --minsup 0.4 --backend list
julia --project=. scripts/mine.jl --input data/toy/basic.txt --output results/bitset.txt --min-count 2 --backend bitset
java -jar tools/spmf.jar run Eclat data/toy/basic.txt results/spmf.txt 40%
julia --project=. scripts/compare_spmf.jl results/basic.txt results/spmf.txt
```

Hai lệnh mining hiện **dừng với lỗi TODO** cho tới khi cài đặt thuật toán. Dữ liệu:
mỗi dòng là một transaction, item ID nguyên dương, tăng dần, không trùng trong dòng.
Output: `1 2 #SUP: 3`. Minsup `0.4` và `40%` cùng nghĩa;
ngưỡng đếm là `ceil(minsup × số transaction)`, điều kiện frequent là `>=`.
Chi tiết interface: [API](docs/API.md).

## Kiểm thử và bằng chứng cuối

Các test mặc định chỉ kiểm tra hạ tầng; hai nhóm test Eclat/SPMF được đánh dấu
**skipped/pending**. M1 bật `ECLAT_TEST_MINER=1`, `ECLAT_TEST_SPMF=1` và dùng backend
`list` mặc định, chưa cần BitVector. Từ M2/final bật cả hai backend như dưới đây,
sau khi cài đặt và tạo 5 reference từ SPMF:

PowerShell:

```powershell
$env:ECLAT_TEST_MINER='1'
$env:ECLAT_TEST_SPMF='1'
$env:ECLAT_TEST_BACKENDS='list,bitset'
julia --project=. tests/runtests.jl
```

Bash / Colab:

```bash
ECLAT_TEST_MINER=1 ECLAT_TEST_SPMF=1 ECLAT_TEST_BACKENDS=list,bitset julia --project=. tests/runtests.jl
```

Không coi scaffold pass là bằng chứng Eclat đúng. Xem
[cách tạo oracle SPMF](tests/reference/spmf/README.md). Trước nộp, bật cả hai nhóm
trong CI và dán **stdout thực tế của lần chạy cuối** vào đây:

```text
TODO FINAL TEST OUTPUT — chưa chạy full suite; chưa có kết quả để công bố.
```

## Tài nguyên và demo

| Tài nguyên công khai | Trạng thái |
|---|---|
| GitHub repository của nhóm | [phuctran33/-DM-Eclat](https://github.com/phuctran33/-DM-Eclat) |
| Google Colab notebook | [Mở từ GitHub](https://colab.research.google.com/github/phuctran33/-DM-Eclat/blob/main/notebooks/demo.ipynb) — chưa cold-run; kiểm quyền public trước nộp |
| Snapshot benchmark trên Hugging Face / Kaggle | TODO: URL + revision/version trong data/manifest.csv |
| Groceries source + mapping tên sản phẩm | TODO: nguồn và phiên bản |
| UCI Splice DNA | [nguồn gốc](https://archive.ics.uci.edu/dataset/69/molecular+biology+splice+junction+gene+sequences) |

Notebook mẫu: [notebooks/demo.ipynb](notebooks/demo.ipynb). Xác minh template local:
**66 kiểm tra hạ tầng/schema pass**, mining/SPMF pending; chi tiết tại
[docs/verification.md](docs/verification.md). Các ô chuẩn bị dữ liệu
phải chạy trong notebook hoặc import helper của repo. Template chưa tải benchmark
và chưa thực hiện remote Colab cold-run.

## Bố cục

```text
src/algorithm/             M1 basic DFS, M2 BitVector (A)
src/applications/          M2 Groceries, association rules, Splice DNA (B; A hỗ trợ rules)
src/structures.jl          Kiểu dữ liệu dùng chung
src/utils.jl               I/O SPMF, minsup và interface mine
scripts/                   CLI, comparator, worker đo đạc, sinh dữ liệu/subset
tests/                     Unit/edge tests, oracle độc lập và SPMF
data/toy/                  5 CSDL nhỏ + expected tự kiểm chứng
data/benchmark/            4 benchmark, không commit file lớn
data/manifest.csv          Nguồn, phiên bản, hash và đường dẫn dữ liệu
configs/                   Tham số thí nghiệm và module
notebooks/demo.ipynb       Colab: setup → M1 → M2 → M3
results/                   CSV, logs, bảng ứng dụng và hình được sinh khi chạy
docs/planning/             Kế hoạch, 9 issue briefs, tiến độ và checklist
docs/paper-notes.md        Ghi chú paper, giải thích DFS adaptation
docs/experiments.md        Giao thức correctness/runtime/RAM/scalability
docs/applications.md       Groceries + DNA, giả định và output cần có
docs/latex/Report.tex      Mẫu báo cáo IEEE tiếng Việt, 3 chương
docs/Report.pdf            Sinh từ LaTeX khi hoàn thiện, chưa có trong template
```

## Quy cách báo cáo và nộp bài

Viết tiếng Việt, **10–15 trang nội dung** theo IEEE conference, không tính tài liệu
tham khảo/phụ lục; đặt PDF cuối tại `docs/Report.pdf`. Trích paper gốc và ít nhất
3 tài liệu khác. Hai ứng dụng chiếm 50% điểm. Nộp một link public GitHub lên Moodle,
README có Colab public và output test cuối; giữ commit history minh bạch.

Xem [ma trận yêu cầu](docs/requirements.md), [hướng dẫn báo cáo](docs/latex/README.md)
và [checklist bàn giao](docs/planning/DELIVERY.md). Mọi người cần hiểu, giải thích
được code và số liệu của nhóm; ghi nguồn và cách sử dụng AI theo yêu cầu môn học.
