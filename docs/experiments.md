# Giao thức thực nghiệm — gói 04 và 07

Owner A, reviewer B. Module 2 pilot, module 3 chạy chính thức.
Thông số khởi đầu ở `configs/experiments.toml`; đây là grid đề xuất, chưa có số đo.

## Dữ liệu và chuẩn hóa

Dùng Chess, Mushroom, Retail, T10I4D100K. B chọn public snapshot ổn định HF/Kaggle,
ghi original source, revision/version, license và SHA-256 trong `data/manifest.csv`.
Chạy thống kê từ file thật: n transactions, m distinct items, mean/max width,
density `mean_width/m`. Không chép số thống kê có thể bị lỗi định dạng trong bảng đề.
SPMF và hai backend phải nhận **cùng byte input**, cùng threshold và xuất đầy đủ.

## Correctness trước performance

Với mỗi dataset/minsup, parse output thành map canonical `itemset -> support`.
Báo missing, extra, wrong_support và exact map equality. Quy ước template:
`exact_match_rate = số key có support đúng / |keys(own) ∪ keys(reference)|`;
hai output rỗng cho rate 1 và phải ghi output size 0. Tỉ lệ cao không thay gate
khớp tuyệt đối. Không chỉ so n_patterns vì hai tập sai vẫn có thể bằng số lượng.
`scripts/compare_spmf.jl` exit 1 khi có khác biệt, exit 2 khi lỗi dữ liệu/lệnh.

## Runtime / output size theo minsup

Mỗi dataset ít nhất 5–7 điểm giảm dần (config dùng 6), pilot trước để tránh output
quá lớn. Chọn grid một lần cho các backend, giữ nguyên trong lần đo chính thức.
Có thể điều chỉnh config sau pilot, nhưng không đổi riêng cho một thuật toán.

Worker `scripts/benchmark_worker.jl INPUT MINSUP BACKEND REPEAT OUTPUT.txt`:

- Compile/warm-up trên dữ liệu nhỏ trước đo; công bố warm-up policy và số lần lặp.
- Timer nội bộ hiện bao gồm đọc file + verticalization/mining, loại ghi output.
- `allocated_bytes` là lượng cấp phát, **không phải peak RAM**.
- Chạy riêng từng tuple dataset/backend/minsup/repeat; lưu stdout CSV, stderr/log.

TODO A: viết runner đọc TOML, vòng lặp 5 lần, timeout/capture exit code, aggregation,
SPMF execution và plotting. Worker hiện không phải runner tự động cho toàn bộ grid.
Benchmark đang gọi miner TODO nên sẽ fail rõ ràng, không tạo số liệu giả.

Để so runtime với SPMF, chọn **một phạm vi đo chung** và ghi rõ: ví dụ external
wall-clock từ lúc khởi động process tới khi ghi output xong, cùng file/disk, nhiều
lần lặp. Đường external wall-clock bao gồm Julia startup/JIT và JVM startup; ghi
nhãn rõ, không diễn giải chênh lệch là riêng chi phí miner. Nếu dùng warm runtime
nội bộ, thêm Java harness/timer cùng ranh giới thay vì so trực tiếp log SPMF với
timer Julia khác phạm vi. Tách cột internal và end-to-end, không gộp vào một metric.

Mỗi đồ thị runtime có basic, BitVector, SPMF; thể hiện median và spread (IQR/min-max),
đơn vị giây và minsup %. Đồ thị output size dùng đầy đủ itemset, thảo luận dense/sparse.
Timeout/OOM là trạng thái riêng, không ghi 0 giây, 0 pattern hoặc bỏ im lặng.

## Peak RAM

Tại `memory_minsup` trung bình cho mỗi dataset, đo **external process peak RSS**
trên từng tiến trình riêng basic/BitVector. Có thể bổ sung SPMF nhưng phải cùng
metric. Dùng OS monitor, giữ log: trên Linux `/usr/bin/time -v` cho max resident set;
Windows có thể dùng process `PeakWorkingSet64` với cách thu thập đủ vòng đời tiến
trình. Không suy RSS từ `@allocated`, và không so trực tiếp SPMF heap log với RSS.
Worker ghi `peak_rss_mib=NA` tới khi monitor bổ sung số thực. Định nghĩa có tính
warm-up/startup hay không vì peak process có thể bao gồm JIT.

## Scalability Retail

`scripts/make_subsets.jl data/benchmark/retail.txt results/subsets 42` tạo nested
samples 10/25/50/75/100% bằng một hoán vị cố định. Giữ relative minsup, không giữ
absolute count; tính lại `ceil(relative*n_subset)` cho từng subset. Đo actual n,
output size và runtime; sampling thay đổi phân bố/threshold nên giải thích giới hạn.

## Ảnh hưởng transaction length

Sinh n=10,000, m=100, widths 5/10/15/20/25/30, seed=42, relative minsup=0.20 cố định.
Lệnh: `julia --project=. scripts/generate_synthetic.jl OUTPUT 100 10000 15 42`.
Generator mẫu chọn items đều không hoàn lại trong từng transaction; không phải IBM
generator của paper. Theo dõi output size cùng runtime vì width tác động số candidate,
support và output. Nếu kết quả quá đơn giản, thêm planted patterns có mô tả đầy đủ.

## Artifacts và phân tích

Lưu raw CSV, per-run logs, file output/correctness summary, hardware/runtime versions,
JAR hash, config snapshot và dataset hashes. Hình cần caption và chú giải. Từ số liệu
giải thích intersection cost, support density, active tidsets và output growth;
đề xuất ≥2 tối ưu cụ thể (ví dụ adaptive list/bitset và buffer reuse/ordering), không
đưa kết luận speedup trước khi đo.
