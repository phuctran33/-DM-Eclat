# Đối chiếu rubric ECLAT

Đối chiếu đề HCMUS, phần giải đáp ngày 25/11/2026 và kết quả Colab ngày
26/11/2026. Trọng số
áp dụng cho Julia là 30 điểm cài đặt, 20 điểm thực nghiệm và 50 điểm ứng dụng.
PASS ghi kết quả kiểm kỹ thuật. Điểm ước lượng để nhóm tự rà soát và điểm
chính thức do giảng viên quyết định. [Đề và rubric](https://hcmus-cs-ta.github.io/lab-book/data-mining/projects/itemset/)

| Mục | Điểm ước lượng | Trạng thái, bằng chứng và vị trí báo cáo |
|---|---:|---|
| A1 · Khớp SPMF | 10/10 | **PASS.** Sorted TID lists, BitVector và DFS chung. Hai backend khớp trọn map của năm toy, kể cả sparse rỗng. Demo chạy lại Java. [Mã](../src/algorithm/) · Ch. 1 |
| A2 · Unit tests | 5/5 | **PASS.** Lệnh đề `julia --project test/runtests.jl`, oracle vét cạn, 20 DB ngẫu nhiên, biên từ máy, lỗi parser và kiểm hai ứng dụng. [Stdout](../README.md#kiem-thu-julia) · Ch. 1, phần kiểm thử |
| A3 · Tối ưu có đo | 10/10 | **PASS.** BitVector tăng tốc warm 5,10× trên Chess và 3,12× trên T10I4D100K ở ngưỡng trung bình. Retail đạt 0,91×, T10 dùng RSS cao hơn Basic. [CSV](../results/raw/optimization.csv) · Ch. 1 và Ch. 2, Bảng VI/VIII |
| A4 · I/O và CLI | 5/5 | **PASS.** SPMF numeric, ngưỡng rational và count, hai backend, lỗi file và alias input/output. [CLI](../scripts/mine.jl) · Ch. 1, phần I/O |
| B1 · Benchmark correctness | 5/5 | **PASS.** 70 phép so trọn map trên 35 cấu hình, 105/105 hash đầu ra khớp đầu ra đã đo. Demo so lại một ngưỡng trung bình mỗi bộ. [Đối chiếu 35 cấu hình](validation/benchmark-maps-2026-11-23.json) · Ch. 2, phần correctness |
| B2 · Runtime, RAM, scalability | 10/10 | **PASS.** 4 bộ × 6 ngưỡng, 5 tập con Retail và 6 độ rộng tổng hợp. 875 lượt OK, có peak RSS, output size và min–max qua 5 lượt. [Phép đo](../results/raw/benchmark_runs.csv) · Ch. 2, các hình và bảng hiệu năng |
| B3 · Phân tích và hướng tối ưu | 5/5 | **PASS.** Giải thích theo mật độ, dựng tidset, output và hai vùng đo. Hai đề xuất cụ thể là tidset thích nghi và gộp AND/popcount. [Phương pháp](experiments.md) · Ch. 2, phần hạn chế |
| C1 · Groceries | 25/25 | **PASS trên Colab CPU.** 9.835 giỏ, 169 item, 1.001 tập, 22 luật, top-10 và ba diễn giải kinh doanh. Kiểm chỉ số và thứ hạng độc lập, khớp Java SPMF. [Notebook](../notebooks/01_groceries.ipynb) · Ch. 3 A–B |
| C2 · Splice DNA | 25/25 | **PASS trên Colab CPU.** 3.185/3.190 mẫu giữ, 48 ID, 381/209/48 tập, 463 ứng viên. Đếm lại theo lớp, 864 count dương dưới ngưỡng và diễn giải GT/AG có nguồn. [Notebook](../notebooks/02_splice_dna.ipynb) · Ch. 3 C–D |
| **Tổng tự đánh giá** | **100/100** | Cả chín tiêu chí trong bảng có bằng chứng, gồm Run all trên Colab cho Demo và hai ứng dụng. Yêu cầu hosting và điều kiện Retail được ghi ở mục nguồn dữ liệu. |

A–B dùng Julia Base/stdlib cho miner. Python chuẩn chuẩn bị dữ liệu, gọi
tiến trình và kiểm bằng chứng. Matplotlib vẽ, IPython hiển thị, nbclient
chạy notebook local/CI. SPMF chỉ là oracle. Mỗi notebook ghi vai trò
thư viện. Ba notebook độc lập dùng kernel Python gọi Julia, phù hợp phần
giải đáp về các ví dụ CLI. Hai thí nghiệm tổng hợp và chia tập con đều cố
định seed 42. Đề cho phép AI hỗ trợ khi sinh viên hiểu và giải thích được
bài làm. [Vấn đáp](DEFENSE_GUIDE.md)

<a id="bao-cao"></a>
## Báo cáo

PDF IEEEtran conference A4, hai cột, 10 trang nội dung tiếng Việt và 1 trang
tham khảo. Có 3 chương, công thức giải thích biến, chú thích/cross-reference
và 12 nguồn gồm Zaki (2000). Giới hạn 10–15 trang tính trên nội dung chính.
Bản này đủ 10 trang nội dung. Hình lấy từ `results/plots/`; bảng
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

**Tải tự động đã kiểm trên Colab, cách áp dụng yêu cầu hosting chờ giảng viên xác nhận.** Đề ưu tiên
bản công khai có sẵn trên Hugging Face hoặc Kaggle và yêu cầu dùng hai nền tảng
này khi benchmark vượt kích thước repo. Trao đổi 25/11 nhấn mạnh tải tự động từ
nguồn bền vững khi server gốc gặp sự cố. Chưa có phúc đáp cuối cho phương án FIMI
có dự phòng. Bốn file chuẩn hóa tổng cộng khoảng 8,49 MiB, file lớn nhất
3,89 MiB. Đề chưa nêu ngưỡng kích thước cụ thể. Demo trên Colab tải đủ cả
bốn bộ từ RPI và từng SHA-256 chuẩn hóa khớp bản đo.
[Đề chính thức](https://hcmus-cs-ta.github.io/lab-book/data-mining/projects/itemset/) · [Bằng chứng tải Colab](validation/colab-2026-11-26.json)

Tra API public của HF/Kaggle theo FIMI, T10I4D100K và các từ khóa itemset,
Retail, Brijs. Các ứng viên chưa xác minh được snapshot và quyền dùng tương ứng.
Demo thử RPI, Antwerp và SPMF theo cấu hình. Kiểm từ cache trống với RPI bị
chặn cho thấy cả bốn đầu vào tải từ Antwerp và khớp hash. Bản SPMF của Chess,
Retail và T10 cũng khớp; Mushroom SPMF trả 8.416 dòng nên bị loại. Khi chặn mọi
nguồn, acquisition thoát khác 0 và giữ nguyên đầu vào đã có và bằng chứng gốc.
[Liên kết tải và SHA-256](../data/README.md#benchmark) · [Cấu hình hiện hành](../configs/datasets.toml)

Retail đã ghi nhận Tom Brijs và bài KDD 1999 trong PDF. Việc gửi bản nộp đầu
và bản cuối kèm tên và ngày công bố đang chờ nhóm xác nhận. Hai kho FIMI chưa
nêu quyền tái phân phối cụ thể cho Chess, Mushroom và T10. Groceries tải từ
snapshot Git đã pin, Splice UCI có CC BY 4.0. Repo dùng các đường dẫn tải
công khai và xuất kết quả phân tích. [Điều kiện Retail](https://www.cs.rpi.edu/~zaki/Workshops/FIMI/data/retail.pdf) ·
[Manifest lịch sử](../data/manifest.csv)

<a id="colab"></a>
## Colab và bàn giao

**PASS trên Google Colab CPU ngày 26/11/2026.** Đã chọn Run all từ các link
GitHub public trên ba runtime Google Compute Engine mới. Các notebook in
`RUNTIME: google-colab` và SHA `9638a157d5d65f3f28184a2133292ff53ab6592f`.
Bản `.ipynb` tải từ Colab có mã các ô khớp commit nguồn, thứ tự thực thi
đầy đủ và 0 lỗi. Bản tóm tắt ghi phiên bản Python, Julia, Java, số kiểm
tra cùng hash của các file tải về và JSON kiểm chứng.
[Bằng chứng nghiệm thu](validation/colab-2026-11-26.json)

| Notebook | Ô đã chạy | Kết quả trên Colab |
|---|---:|---|
| [Demo](https://colab.research.google.com/github/phuctran33/-DM-Eclat/blob/main/notebooks/demo.ipynb) | 7/7 | 792 kiểm tra Julia, 5 toy và 4 benchmark khớp SPMF, 8 hình, 46 artifact hashes và hash PDF |
| [Groceries](https://colab.research.google.com/github/phuctran33/-DM-Eclat/blob/main/notebooks/01_groceries.ipynb) | 4/4 | 1.001 tập khớp SPMF, 22 luật, top-10 và biểu đồ độ rộng |
| [Splice DNA](https://colab.research.google.com/github/phuctran33/-DM-Eclat/blob/main/notebooks/02_splice_dna.ipynb) | 4/4 | 381/209/48 tập khớp SPMF, 463 ứng viên và biểu đồ support |

Mở mỗi link trong runtime CPU mới, chọn **Run all** và đối chiếu
`SOURCE COMMIT` với public main. Giữ stdout phiên bản runtime và tải
`.ipynb` có output cùng các JSON tương ứng dưới `OUTPUT` trước khi ngắt
runtime. Local runner tạo `delivery-validation.json` khi cả ba cùng chạy
từ một checkout.
[Xem CI](https://github.com/phuctran33/-DM-Eclat/actions)

Repo GitHub công khai. README có tên, MSSV, phân công, link ba notebook,
hướng dẫn có ví dụ và stdout 792 kiểm tra Julia. Phần chuẩn bị dữ liệu
chạy trong notebook qua script của nhóm. Đề gợi ý Group ID ở repo root. Nhóm
cần đối chiếu thông báo lớp về Group ID và thời hạn, rồi nộp đúng một URL
GitHub công khai trên Moodle sau khi nghiệm thu.

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
