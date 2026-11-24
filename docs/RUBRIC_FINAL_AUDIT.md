# Đối chiếu rubric và nghiệm thu ECLAT

Đối chiếu đề gốc ngày 23/11/2026 với bản tích hợp sau PR #5 và lần rà
nghiệm thu cuối. Bảng áp dụng trọng số cho bản Julia. PASS ghi tiêu chí có
bằng chứng kỹ thuật trong phạm vi đã kiểm. Mức điểm chính thức do giảng
viên quyết định.
[Rubric HCMUS](https://hcmus-cs-ta.github.io/lab-book/data-mining/projects/itemset/) ·
[PR #5](https://github.com/phuctran33/-DM-Eclat/pull/5)

| Tiêu chí | Điểm ước lượng | Trạng thái và bằng chứng | Vị trí PDF, giới hạn |
|---|---:|---|---|
| A1 · Đúng toàn bộ với SPMF | 10/10 | **PASS.** Vertical tidsets, giao, prefix DFS và prune trong `src/algorithm/`. Năm toy tại 40% khớp toàn bộ itemset/support (basic 7, boundary 4, dense 14, duplicates 5, sparse 0). `test_spmf.jl` và Java 2.64b pin hash. | Ch. 1, tr. 1–3. Kết quả 100% trong phạm vi kiểm, bổ sung lập luận tính đủ/duy nhất. |
| A2 · Unit tests tự động | 5/5 | **PASS.** `julia --project test/runtests.jl` và `julia --project=. tests/runtests.jl` cho cùng 16 nhóm test, 792/792 checks trên macOS. Gồm oracle vét cạn, 20 random DB, ownership, tails 63/64/65/127/128/129 và tests ứng dụng. [Stdout](../README.md#stdout-kiểm-thử-julia-cuối). | Ch. 1 mục I, tr. 3. CI dùng lệnh trong đề. |
| A3 · Tối ưu có đo lường | 10/10 | **PASS.** `bitset.jl` chỉ cấp masks cho frequent singletons, giữ DFS chung. Warm median speedup 5,10 / 1,73 / 0,91 / 3,12 tại medium minsup. [CSV](../results/raw/optimization.csv). | Ch. 1 mục G–H và Ch. 2 Bảng VI/VIII, tr. 3, 5–6. Retail chậm hơn, T10 dùng RSS cao hơn. |
| A4 · I/O và CLI SPMF | 5/5 | **PASS.** `utils.jl`, `scripts/mine.jl`, `test_io.jl`, `test_support.jl`, `test_cli.jl`. Rational boundary, output canonical, lỗi input, hai backend và khóa ghi đè vào input/alias. | Ch. 1 mục E, tr. 2. Numeric SPMF, ID dương và tăng theo dòng. |
| B1 · Correctness trên benchmark | 5/5 | **PASS.** 70 map comparisons lưu trữ. Kiểm lại mới cả 35 cases cùng normalized input SHA-256 và absolute count. 105/105 output hashes khớp output của các lượt end-to-end đã công bố. [Đối chiếu mới](validation/benchmark-maps-2026-11-23.json). | Ch. 2 mục D và Bảng V, tr. 4–5. Không cần đo lại thời gian để xác minh output. |
| B2 · Runtime, RAM, scalability | 10/10 | **PASS.** 4 tập × 6 ngưỡng, 5 nested subsets, 6 widths, 875 measurements OK. Kiểm 46 hashes, CSV summary, OS RSS và process logs. [Protocol](experiments.md) · [Plots](../results/plots/). | Ch. 2 mục E–J, tr. 4–9. Min–max qua 5 lượt, dữ liệu một máy. |
| B3 · Phân tích và tối ưu tiếp | 5/5 | **PASS.** Giải thích mật độ, output size, thời gian theo hai scopes, warm-up và allocation/RSS. Đề xuất mixed list/bitmap theo density và fused AND/popcount với buffer theo depth. | Ch. 2 mục K, tr. 8–9. Hướng tiếp theo cần profile và đo riêng. |
| C1 · Ứng dụng giỏ hàng | 23/25 | **PASS kỹ thuật, chờ Colab public.** `groceries.jl`, `rules.jl`, `pipelines.jl`, `export_rules.jl`. 9.835 giỏ, 169 items, 1.001 tập, 22 luật và top-10 tính đúng. Auditor độc lập kiểm metrics, mọi split, thứ hạng và SPMF. | Ch. 3 mục A–B/E, tr. 9–10. Ba luật hạng 1/5/9 có support/confidence/lift và đề xuất thử nghiệm. Có 580 giỏ thỏa tiền kiện và 353 giỏ thỏa đầy đủ ít nhất một luật top-10. |
| C2 · Ứng dụng mẫu sinh học | 23/25 | **PASS kỹ thuật, chờ Colab public.** `dna.jl`, `compare_dna.jl`, `pipelines.jl`. 3.190 raw, giữ 3.185, 48 IDs, 381/209/48 patterns, 463 candidates, 864 count dương dưới ngưỡng. Recount và SPMF theo lớp. | Ch. 3 mục C–E, tr. 9–10. Giải thích GT/AG và phân biệt ranh giới EI/IE với tâm cửa sổ đối chứng N. |
| **Tổng** | **96/100** | Ước lượng tạm thời, giữ lại 2 điểm mỗi ứng dụng đến khi có Run all từ public main. | |

## Kiến trúc và bảo trì

- `scripts/mine.jl` đi qua API Julia, parser SPMF và một DFS dùng chung
  cho list/BitVector. Hai ứng dụng gọi API qua `pipelines.jl`. Python và
  Java kiểm lại pattern/support, metrics và thứ hạng độc lập.
- `benchmark_runner.py` phụ trách kế hoạch chạy, preflight, checkpoint,
  timeout và CSV. Worker Julia giữ phần đo trong process. `plot_results.py`
  và `application_tables.py` đọc kết quả đã lưu để tạo hình và bảng.
- `benchmark_runner.py` và `verify_application_results.py` cần đọc cùng sơ đồ
  luồng vì chứa nhiều bước. Cách tách runner, worker, oracle và báo cáo
  phù hợp với trách nhiệm từng bước. Một số chỗ đọc định dạng SPMF ở
  Julia/Python cần giữ đồng nhất khi đổi format. Lần rà này chưa thấy lệch.
- Các script tạo reference, test riêng của B và bản LaTeX review A phục vụ
  tái tạo oracle, kiểm theo phạm vi và truy nguồn. Đã đánh dấu nhật ký
  kiểm chứng là tài liệu lịch sử. [Kiến trúc](ARCHITECTURE.md) ·
  [Nhật ký lịch sử](verification.md)

## Kiểm chứng chéo

- **Core.** Kiểm điều kiện `support >= min_count`, list two-pointer, mask mới
  mỗi giao, tail words và repeated rows. CLI dùng count chính xác và nhận diện
  input/output cùng file qua `samefile`. Oracle Java chỉ dùng để đối chiếu.
  Bản điều chỉnh DFS bám nguyên lý prefix và giao tidsets của Zaki.
  [Paper](https://cs.rpi.edu/~zaki/PaperDir/TKDE00.pdf) ·
  [Ghi chú thuật toán](paper-notes.md)
- **Benchmark.** Đảo offset 0/1 thu lại đúng từng dòng từ raw đã kiểm hash.
  Giữ nguyên 24 cặp dataset/minsup, 5 Retail subsets cùng permutation và
  6 width cases seed 42 với hoán vị ghép cặp theo từng giao dịch. Mỗi case
  chạy một lần list, bitset và SPMF để so
  map và hash, dùng cùng input đã đo. Hash output khớp với cả 5 lượt đo
  end-to-end của backend tương ứng. Snapshot phép đo là `49dafc9`.
  [Dữ liệu gốc và hash](../results/raw/dataset_provenance.json) ·
  [Audit metadata](../results/raw/protocol.json)
- **Số đo.** RSS Basic/BitVector là 304,4/259,1 MiB với Chess, 271,6/259,0 với
  Mushroom, 291,4/280,0 với Retail và 345,1/351,1 với T10. Chênh lệch snapshot
  lần lượt là giảm 14,88%, 4,63%, 3,89% và tăng 1,74%. Allocation chỉ tính
  byte cấp phát trong vùng Julia. End-to-end có startup, JIT/JVM và I/O.
  [RSS CSV](../results/raw/memory_comparison.csv)
- **Ứng dụng.** Live checks chạy lại preprocessing, mining và Java cho
  Groceries cùng ba lớp Splice. Final gate yêu cầu đúng một bản ghi SPMF
  cho mỗi đầu vào. Nó đối chiếu hash output mới với metadata đã công bố và
  kiểm từng bảng/pattern đã commit. Tải Splice từ ZIP chính thức của UCI khi
  mirror không dùng được, với cùng SHA-256 cho dữ liệu đã giải nén.
  [Bảng và provenance ứng dụng](../results/applications/)
- **Regression từ review Phúc.** Controller từ chối overwrite trước ghi.
  Timeout Linux/macOS dừng process group và wait. Windows bị từ chối ở
  preflight phần đo. Test bảng giả lập CP1252 xác nhận file UTF-8 vẫn đúng.

<a id="bao-cao"></a>
## Báo cáo

**PASS định dạng và nội dung kỹ thuật.** Build Tectonic 0.17.0,
IEEEtran conference A4, hai cột, 10 trang nội dung và 1 trang tài liệu tham khảo.
Đã render PDF phát hành và xem 11/11 trang ở lần rà cuối. Công thức, dấu
tiếng Việt, hình, bảng và bibliography đọc được theo thứ tự hai cột.
Đã đối chiếu số hiện trong PDF với bảng LaTeX và CSV benchmark, top-10
Groceries và DNA. Final TeX log sạch overfull, missing glyph và undefined
citation/reference. Mười một nguồn gồm Zaki, Agrawal–Srikant, SPMF, Julia,
FIMI, Brijs, nguồn hai ứng dụng và nghiên cứu dinucleotide GT/AG của Burset
và cộng sự. Link hỏng của Brijs được thay bằng DOI đã đối chiếu Crossref.

Build metadata lưu SHA-256 của PDF và đối chiếu toàn bộ nguồn, ảnh và bảng đang dùng.
Báo cáo và build log ngày 17/11 là bằng chứng của snapshot M3 cũ.
[PDF](Report.pdf) · [Nguồn và lệnh build](latex/README.md) ·
[Hash nguồn](report-build.json) ·
[PDF snapshot cũ](https://github.com/phuctran33/-DM-Eclat/blob/392d165b897eea7c78d9ce2076b5e05ac0c0e7c7/docs/Report.pdf)

<a id="dataset-hosting"></a>
## Dataset hosting

Đề yêu cầu host trên Hugging Face hoặc Kaggle với dữ liệu benchmark vượt
kích thước repository. Đề không nêu ngưỡng riêng của môn. File normalized
lớn nhất là Retail, khoảng 3,89 MiB. Cả bốn file nằm dưới giới hạn
100 MiB/file của GitHub. Đã tải lại cả bốn URL FIMI công khai và kiểm
SHA-256 của gzip gốc và TXT normalized. Pipeline tải FIMI đáp ứng việc
tái lập với đúng dữ liệu đã đo.
[Rubric](https://hcmus-cs-ta.github.io/lab-book/data-mining/projects/itemset/) ·
[Giới hạn GitHub](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github)

| FIMI | Giao dịch | Items | Raw gzip bytes | Normalized bytes |
|---|---:|---:|---:|---:|
| Chess | 3.196 | 75 | 14.253 | 339.098 |
| Mushroom | 8.124 | 119 | 34.370 | 562.284 |
| Retail | 88.162 | 16.470 | 1.636.819 | 4.080.775 |
| T10I4D100K | 100.000 | 870 | 1.374.931 | 3.922.248 |

Lần rà trước đã tìm qua web và APIs HF/Kaggle với `FIMI`, `SPMF`, `T10I4D100K`,
`frequent itemset`. Các bộ Kaggle liên quan chứa basket/store CSV, sequences
hoặc dữ liệu synthetic khác. Chưa tìm được bản trùng dữ liệu đầu vào đã đo có
quyền tái phân phối xác minh được. Giữ config nguồn và manifest FIMI. Nếu nhóm
có bản mirror được phép dùng, kiểm raw hoặc normalized SHA-256 trước khi thêm
URL. Retail yêu cầu ghi nguồn Brijs và gửi bản nộp đầu cùng bản cuối cho
bên cung cấp. FIMI không ghi rõ quyền tái phân phối cho ba file còn lại.
[Kho FIMI](https://www.cs.rpi.edu/~zaki/Workshops/FIMI/data/) ·
[Manifest](../data/manifest.csv) ·
[Điều kiện Retail](https://www.cs.rpi.edu/~zaki/Workshops/FIMI/data/retail.pdf)

Nếu cần xác nhận quy định với giảng viên, hỏi liệu bốn file dưới 4 MiB có
thể dùng URL FIMI công khai, SHA-256 và mã tải Colab, hoặc môn có ngưỡng
riêng yêu cầu bản mirror HF/Kaggle.

## Notebook và nghiệm thu

| Môi trường | Bằng chứng |
|---|---|
| Local macOS | 7/7 cells ở bản tích hợp. Julia 1.10.10, Java 23.0.1, SPMF 2.64b. 792 Julia checks và final gate pass. |
| CI | Julia 1.9/1.11/1.12, Python controller, plot, delivery tests và notebook Ubuntu theo [GitHub Actions](https://github.com/phuctran33/-DM-Eclat/actions). |
| Google Colab 17/11 | 7/7 cells thật từ Git bundle M3 `ee2d46d`, Julia 1.12.6, 790 checks, tám live input maps và PDF gate. [Notebook, log và hash](member-b-validation/m3/colab/README.md). |
| Google Colab public main | **NOT VERIFIED Run all.** Đã mở notebook công khai. Cần Run all trong runtime mới và lưu output 7 cells cùng `delivery-validation.json`. [Các bước lấy bằng chứng](planning/DELIVERY.md#colab-public-main). |

Phạm vi kỹ thuật có bằng chứng cho hai chương đầu và kết quả của hai ứng
dụng. Để hoàn tất nghiệm thu, xác nhận Colab public, thông tin nhóm/hạn
Moodle và điều kiện sử dụng Retail. Xác nhận hosting nếu môn đặt thêm
ngưỡng cho các file nhỏ.
[Checklist nghiệm thu](planning/DELIVERY.md) · [Vấn đáp](DEFENSE_GUIDE.md)
