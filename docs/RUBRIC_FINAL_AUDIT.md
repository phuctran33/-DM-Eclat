# Đối chiếu rubric ECLAT

Đối chiếu đề HCMUS ngày 24/11/2026. Trọng số áp dụng cho bài Julia. PASS ghi
kết quả kiểm kỹ thuật. Điểm là ước lượng của nhóm, giảng viên quyết định
điểm chính thức. [Đề và rubric](https://hcmus-cs-ta.github.io/lab-book/data-mining/projects/itemset/)

| Mục | Điểm ước lượng | Trạng thái, bằng chứng và vị trí báo cáo |
|---|---:|---|
| A1 · Khớp SPMF | 10/10 | **PASS.** Sorted TID lists, BitVector và DFS chung. Hai backend khớp trọn map của năm toy, kể cả sparse rỗng. Demo chạy lại Java. [Mã](../src/algorithm/) · Ch. 1 |
| A2 · Unit tests | 5/5 | **PASS.** Lệnh đề `julia --project test/runtests.jl`, oracle vét cạn, 20 DB ngẫu nhiên, biên từ máy, lỗi parser và kiểm hai ứng dụng. [Stdout](../README.md#kiem-thu-julia) · Ch. 1, phần kiểm thử |
| A3 · Tối ưu có đo | 10/10 | **PASS.** BitVector tăng tốc warm 5,10× trên Chess và 3,12× trên T10I4D100K ở ngưỡng trung bình. Retail đạt 0,91×, T10 dùng RSS cao hơn Basic. [CSV](../results/raw/optimization.csv) · Ch. 1 và Ch. 2, Bảng VI/VIII |
| A4 · I/O và CLI | 5/5 | **PASS.** SPMF numeric, ngưỡng rational và count, hai backend, lỗi file và alias input/output. [CLI](../scripts/mine.jl) · Ch. 1, phần I/O |
| B1 · Benchmark correctness | 5/5 | **PASS.** 70 phép so trọn map trên 35 cấu hình, 105/105 hash đầu ra khớp đầu ra đã đo. Demo so lại một ngưỡng trung bình mỗi bộ. [Đối chiếu 35 cấu hình](validation/benchmark-maps-2026-11-23.json) · Ch. 2, phần correctness |
| B2 · Runtime, RAM, scalability | 10/10 | **PASS.** 4 bộ × 6 ngưỡng, 5 tập con Retail và 6 độ rộng tổng hợp. 875 lượt OK, có peak RSS, output size và min–max qua 5 lượt. [Phép đo](../results/raw/benchmark_runs.csv) · Ch. 2, các hình và bảng hiệu năng |
| B3 · Phân tích và hướng tối ưu | 5/5 | **PASS.** Giải thích theo mật độ, dựng tidset, output và hai vùng đo. Hai đề xuất cụ thể là tidset thích nghi và gộp AND/popcount. [Phương pháp](experiments.md) · Ch. 2, phần hạn chế |
| C1 · Groceries | 23/25 | **PASS kỹ thuật, Colab cuối chưa xác minh.** 9.835 giỏ, 169 item, 1.001 tập, 22 luật, top-10 và ba diễn giải kinh doanh. Kiểm chỉ số và thứ hạng độc lập, khớp Java SPMF. [Notebook](../notebooks/01_groceries.ipynb) · Ch. 3 A–B |
| C2 · Splice DNA | 23/25 | **PASS kỹ thuật, Colab cuối chưa xác minh.** 3.185/3.190 mẫu giữ, 48 ID, 381/209/48 tập, 463 ứng viên. Đếm lại theo lớp, 864 count dương dưới ngưỡng và diễn giải GT/AG có nguồn. [Notebook](../notebooks/02_splice_dna.ipynb) · Ch. 3 C–D |
| **Tổng** | **96/100** | Tạm giữ 2 điểm mỗi ứng dụng trong khi chờ chạy cả ba notebook cuối trên Colab. |

A–B dùng Julia Base/stdlib cho miner. Python chuẩn chuẩn bị dữ liệu, gọi
tiến trình và kiểm bằng chứng. Matplotlib vẽ, IPython hiển thị, nbclient
chạy notebook local/CI. SPMF chỉ là oracle. Mỗi notebook ghi rõ vai trò
thư viện theo giải đáp của giảng viên. Ba notebook độc lập áp dụng khuyến
nghị tách demo và hai ứng dụng. Đề cho phép AI hỗ trợ khi sinh viên hiểu
và giải thích được bài làm. [Vấn đáp](DEFENSE_GUIDE.md)

<a id="bao-cao"></a>
## Báo cáo

PDF IEEEtran conference A4, hai cột, 10 trang nội dung tiếng Việt và 1 trang
tham khảo. Có 3 chương, công thức giải thích biến, chú thích/cross-reference
và 11 nguồn gồm Zaki (2000). Hình lấy trực tiếp từ `results/plots/`; bảng
ứng dụng tạo từ CSV. Script kiểm số trang và log biên dịch, lưu SHA-256
của PDF cùng nguồn và hình. [PDF](Report.pdf) · [Build](../README.md#build-bao-cao) ·
[Hash nguồn](report-build.json)

<a id="dataset-hosting"></a>
## Nguồn dữ liệu

| Benchmark FIMI | Giao dịch | Items | Gzip (bytes) | Chuẩn hóa (bytes) |
|---|---:|---:|---:|---:|
| Chess | 3.196 | 75 | 14.253 | 339.098 |
| Mushroom | 8.124 | 119 | 34.370 | 562.284 |
| Retail | 88.162 | 16.470 | 1.636.819 | 4.080.775 |
| T10I4D100K | 100.000 | 870 | 1.374.931 | 3.922.248 |

Đề nêu HF/Kaggle cho dữ liệu benchmark vượt kích thước repo và ưu tiên
bản công khai sẵn có. File lớn nhất khoảng 3,89 MiB, dưới giới hạn GitHub
100 MiB/file. Môn không ghi ngưỡng riêng. Nếu cần xác nhận, hỏi liệu bốn
file dưới 4 MiB có thể dùng URL FIMI và checksum hay môn cần mirror theo
quy định riêng. Cả bốn URL đã tải và kiểm đúng hash; bản chuẩn hóa chỉ
thay khoảng trắng và cộng 1 vào ID của Retail/T10. [Rubric](https://hcmus-cs-ta.github.io/lab-book/data-mining/projects/itemset/) ·
[Giới hạn GitHub](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github) ·
[Hash đầu vào](../results/raw/dataset_provenance.json)

Retail đã ghi nguồn Brijs trong PDF. Nhóm còn cần gửi bản nộp đầu và bản
cuối cho bên cung cấp theo hướng dẫn nguồn. FIMI chưa ghi rõ quyền tái
phân phối cho Chess, Mushroom và T10. Groceries tải từ snapshot Git đã
pin, Splice UCI có CC BY 4.0. Repo tải raw tại chỗ, công bố kết quả đã
phân tích. [Điều kiện Retail](https://www.cs.rpi.edu/~zaki/Workshops/FIMI/data/retail.pdf) ·
[Manifest](../data/manifest.csv)

<a id="colab"></a>
## Colab và bàn giao

**BLOCKED — actual Colab execution not verified** cho ba notebook cuối.
Chạy kernel Jupyter sạch và CI Ubuntu là hai bằng chứng khác môi trường.
Các phiên Colab notebook tích hợp trước đây chỉ xác nhận bản cũ.

| Notebook | Bằng chứng cần lưu từ Colab public main |
|---|---|
| [Demo](https://colab.research.google.com/github/phuctran33/-DM-Eclat/blob/main/notebooks/demo.ipynb) | Notebook có output, `benchmark-review/review.json`, 5 toy, 4 benchmark live và hash PDF |
| [Groceries](https://colab.research.google.com/github/phuctran33/-DM-Eclat/blob/main/notebooks/01_groceries.ipynb) | Notebook có output, `applications/validation.json`, `SPMF PASS groceries 1001` và top-10 |
| [Splice DNA](https://colab.research.google.com/github/phuctran33/-DM-Eclat/blob/main/notebooks/02_splice_dna.ipynb) | Notebook có output, `applications/validation.json` và `SPMF PASS` cho EI, IE, N |

Mở mỗi link trong runtime CPU mới, chọn **Run all**, giữ output và ghi
`SOURCE COMMIT` từ ô đầu. Mỗi notebook in đường dẫn bằng chứng. Tải bản
`.ipynb` có kết quả và JSON trước khi ngắt runtime. Local runner tạo
`delivery-validation.json` khi cả ba cùng chạy từ một checkout.
[Xem CI](https://github.com/phuctran33/-DM-Eclat/actions)

README có tên, MSSV, phân công, link public, hướng dẫn chạy và stdout kiểm
thử. Hai thành viên kiểm Group ID, thời hạn và nộp một URL GitHub công khai
trên Moodle theo thông báo lớp.

## Bằng chứng gốc trong Git

Các file làm việc cũ được truy xuất theo commit
`556602e66d79f90fa735100e4c58fd0ba59e6d91`. Manifest gốc 46 mục và archive
log vẫn được kiểm. Audit kiểm các bản PNG và bảng LaTeX rời cũ bằng byte trong Git.
Báo cáo dùng PDF hình trong `results/plots/`. Demo sinh PNG từ CSV đã đo vào
thư mục phiên chạy. Hai file bảng LaTeX mới giữ nội dung của mười bảng cũ. Snapshot nguồn đo
là `49dafc999b6c00f8c4275ee68f99d4a6e3046f3d`.

- [Colab M3 từ Git bundle](https://github.com/phuctran33/-DM-Eclat/tree/556602e66d79f90fa735100e4c58fd0ba59e6d91/docs/member-b-validation/m3/colab)
- [Java SPMF độc lập cho toy](https://github.com/phuctran33/-DM-Eclat/tree/556602e66d79f90fa735100e4c58fd0ba59e6d91/docs/member-b-validation/spmf)
- [Bản review chương 1–2](https://github.com/phuctran33/-DM-Eclat/blob/556602e66d79f90fa735100e4c58fd0ba59e6d91/docs/Member-A-review.pdf) ·
  [Nhật ký trước khi gộp](https://github.com/phuctran33/-DM-Eclat/blob/556602e66d79f90fa735100e4c58fd0ba59e6d91/docs/verification.md)
- [Log Java SPMF của ứng dụng](https://github.com/phuctran33/-DM-Eclat/tree/0dcd64903eb5667c249cdf26501c4529b260c3f2/results/applications/verification)
- [Manifest đo gốc](../results/raw/artifact_sha256.csv) ·
  [PR #7 sửa báo cáo và fallback UCI](https://github.com/phuctran33/-DM-Eclat/pull/7)
