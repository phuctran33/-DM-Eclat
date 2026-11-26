# Đối chiếu rubric ECLAT

Các mục dưới đây dẫn đến phần báo cáo, mã và số liệu mà người chấm có thể kiểm lại. [Rubric HCMUS](https://hcmus-cs-ta.github.io/lab-book/data-mining/projects/itemset/) · [Báo cáo PDF](Report.pdf)

| Tiêu chí | Vị trí và bằng chứng |
|---|---|
| A1–A2 · Cài đặt đúng và kiểm thử | Chương 1. Hai backend đối chiếu toàn bộ itemset và support với vét cạn và năm bộ toy SPMF. [Test miner](../tests/test_miner.jl) · [Đầu ra bộ test Julia](../README.md#kiem-thu-julia) |
| A3–A4 · Tối ưu, đọc ghi SPMF và CLI | Chương 1. [DFS và phép giao](../src/algorithm/) · [Lệnh chạy](../scripts/mine.jl) · [Đo riêng thay đổi tiền tố](experiments.md#dfs-prefix) |
| B1 · Kiểm chứng trên benchmark | Chương 2. 70 phép so toàn bộ itemset/support ở 35 cấu hình. [CSV](../results/correctness/comparisons.csv) · [Đối chiếu 105 đầu ra](validation/benchmark-maps-2026-11-23.json) |
| B2–B3 · Thời gian, bộ nhớ, khả năng mở rộng và nhận xét | Chương 2. Bốn bộ × sáu ngưỡng, năm kích thước Retail và sáu độ rộng tổng hợp. SPMF có trung vị đầu cuối thấp nhất ở 23/24 điểm trên bốn bộ chính. [875 phép đo](../results/raw/benchmark_runs.csv) · [Hình](../results/plots/) · [Giao thức](experiments.md) |
| C1 · Groceries | Chương 3. 9.835 giỏ, 1.001 tập phổ biến, 22 luật và diễn giải các luật đứng đầu. [Notebook](../notebooks/01_groceries.ipynb) · [Top 10](../results/applications/groceries_top10.csv) |
| C2 · Splice DNA | Chương 3. 3.185 mẫu hợp lệ, 381/209/48 tập phổ biến ở ba lớp EI/IE/N và 463 mẫu được so sánh. [Notebook](../notebooks/02_splice_dna.ipynb) · [Bảng kết quả](../results/applications/dna_patterns.csv) |

<a id="colab"></a>

Ba notebook đã chạy trên ba phiên Colab CPU mới ngày 26/11/2026 ở commit `9638a15`. Hồ sơ ghi phiên bản runtime, số ô và SHA-256 của output theo đúng phiên đó. [Bằng chứng Colab](validation/colab-2026-11-26.json) · [GitHub Actions](https://github.com/phuctran33/-DM-Eclat/actions)

<a id="bao-cao"></a>

PDF có ba chương. Lệnh build kiểm số trang nội dung, trích dẫn, font và tràn khung. [Hướng dẫn build](../README.md#build-bao-cao) · [SHA-256 và số trang của bản hiện hành](report-build.json)

<a id="dataset-hosting"></a>

Bốn benchmark tải tự động từ nguồn công khai và được kiểm bằng SHA-256. Bốn file chuẩn hóa chiếm tổng cộng 8,49 MiB. Nhóm cần tự xác nhận việc nộp URL trên Moodle và việc gửi bản đầu, bản cuối theo điều kiện sử dụng Retail. [Nguồn, kích thước và điều kiện](../data/README.md#benchmark)
