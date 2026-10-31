# Giao thức và tái lập thực nghiệm Member A

Cài đặt đo: commit trong `results/raw/environment.json`; mã nguồn tác động phép đo
được hash trong `results/raw/protocol.json`. Figures/tables được render sau lần đo;
chỉnh sửa trình vẽ không đổi CSV gốc. Bản đo 31/10/2026 dùng Apple M1, RAM 8 GiB,
macOS 14.6.1 arm64, Julia 1.10.10/1 thread, Java 23.0.1, SPMF 2.64b, Python 3.14.0.
Không coi các con số này là cấu hình bắt buộc của API Julia ≥1.9.

## Dữ liệu

`python3 scripts/acquire_benchmarks.py` tải bản FIMI từ nguồn học thuật gốc,
kiểm raw SHA-256 trong `configs/datasets.toml`, giải gzip theo magic bytes và tạo
file numeric SPMF. Không lấy một bản Hugging Face/Kaggle chưa xác minh để gọi là
snapshot chuẩn: đã tìm nhưng không xác định được bộ bốn phù hợp. Bản FIMI được
pin theo **nội dung**, không có revision Git do nguồn không cung cấp.

Retail và T10I4D100K: cộng **1 cho mọi item ID**, vì raw có 0 và shared parser chỉ
nhận ID dương. Chess/Mushroom không đổi ID. Chỉ chuẩn hóa whitespace; không bỏ,
gộp hay sắp lại transaction rows. Raw đã sorted/unique trong từng dòng; bất ngờ
khác định dạng làm acquisition fail. Ba backend dùng cùng file normalized.

Provenance, transformations, normalized hashes và số byte:
`results/raw/dataset_provenance.json`; nguồn/license trong `data/manifest.csv`.
`dataset_statistics.csv` tính từ file đang dùng: actual n, distinct m, mean/max
width, density=mean_width/m. Không commit raw datasets hoặc JAR.
FIMI không ghi license rõ cho mọi tập; ghi đúng trạng thái đó. Retail được credit
Tom Brijs và trích Brijs et al. (KDD 1999, pp. 254–260), theo điều kiện tại
https://www.cs.rpi.edu/~zaki/Workshops/FIMI/data/retail.pdf; việc gửi
bản nghiên cứu cho donor chưa được tự động thực hiện.

## Correctness gate

Mỗi dataset/minsup chạy preflight list, bitset, SPMF với output đầy đủ, parse strict
map `itemset -> absolute support`, reject duplicate output và so toàn bộ map.
`results/correctness/comparisons.csv` giữ đúng header schema v1.0.0. Missing, extra,
wrong_support phải đều 0. Match rate dùng số key có support đúng chia union keys;
hai maps rỗng cho rate 1. Tỉ lệ 100% trên output rỗng không thay cho cases có output.

Julia tính τ=ceil(θn) chính xác. SPMF nhận double; runner gửi θ'=(τ−0.5)/n để
ceil(double(θ')*n)=τ, tránh boundary drift. Đây là **cùng absolute minsup**, không
đổi tập frequent. Tham số thật ghi trong mỗi command JSON, kiểm count bins bằng test.
Toy references thật giữ 40% như hợp đồng; regenerate bằng
`python3 scripts/prepare_spmf.py --references`. Manifest có input/output/JAR hashes,
Java/SPMF version và command. SPMF 2.64b cần Java ≥21; JAR latest yêu cầu Java mới
hơn máy đo nên không dùng. Không đọc hoặc sao chép source thuật toán SPMF.

Mỗi timed output được so toàn bộ với preflight đã xác minh; internal worker kiểm
map ở mọi repetition. Lỗi equality không được diễn giải thành speedup. Preflight
failed được ghi đúng lần thử thực, không biến thành năm repetitions giả; runner
chuyển sang các cases còn lại. Mọi lỗi/timeout/OOM có log và trạng thái riêng.

## Phạm vi đo

| Scope | Backends | Công việc trong timer |
|---|---|---|
| end_to_end | list, bitset, spmf | Process mới, runtime/JIT/JVM startup, read, mine, write, OS monitor/controller wait |
| internal_read_mine | list, bitset | Sau warm-up đầy đủ case: read, validation, verticalization, DFS; không write/verification/GC chủ động |

End-to-end dùng Python perf_counter quanh Popen/wait, chung boundary cho cả ba
backend. Preflight là một warm-up process riêng (đồng thời làm ấm file cache);
startup vẫn có trong mỗi timed process. Timeout-wait của Python có polling với
độ trễ cuối có thể đến khoảng 50 ms; metric này là wall time harness quan sát,
không timer chỉ của miner. Không trừ timer các phạm vi để suy thời gian JIT.

Internal: một process/case/backend; warm tiny case rồi warm toàn bộ dataset/case
một lần; GC.gc() trước mỗi trong 5 lần @timed read+mine. Worker giữ reference map
của warm-up, kiểm và serialize sau timer. Không dùng SPMF log timer để tạo đường
internal vì chưa có Java warm harness tương đương. `allocated_bytes` là tổng
allocation trong vùng @timed, không phải peak RSS.

Raw rows giữ schema trong `schemas/contracts.toml`; run_id unique, seed 42,
repetition và scope riêng. Aggregate median/min/max và n_ok/n_timeout/n_oom/n_error.
Biểu đồ error bars dùng **min–max**, không gọi là confidence intervals. Speedup
=median_basic/median_bitvector, chỉ cùng input/min_count/scope và số đo hợp lệ.
Không dùng 0 cho metric thiếu. Không che các cấu hình thất bại hoặc output bằng 0.

Peak RSS lấy bằng BSD `/usr/bin/time -l` trên macOS hoặc GNU `time -v` trên Linux,
bao toàn vòng đời process end-to-end; đổi về MiB bằng đơn vị OS tương ứng. Có cả
startup/JIT, input, active tidsets, output/writer. Batch internal không có RSS riêng
cho từng repetition nên ghi NA. Không so RSS với heap log SPMF. SIGKILL đơn thuần
không được gán OOM nếu không có thông báo hỗ trợ; timeout giết cả process group.

## Các grid

- Runtime/output: Chess, Mushroom, Retail, T10I4D100K; 6 ngưỡng/tập trong TOML;
  list/bitset/spmf; 5 repetitions mỗi điểm. Memory lấy đúng memory_minsup có trong grid.
- Retail scalability: nested prefixes của cùng randperm(MersenneTwister(42)),
  10/25/50/75/100%; giữ θ=0.01, tính lại τ theo actual n. Subset 100% là hoán vị
  của toàn bộ dữ liệu; không mặc định output size monotone giữa samples khác n.
- Transaction length: n=10,000, m=100, widths=5/10/15/20/25/30, seed=42, θ=0.20.
  Generator uniform không hoàn lại, không phải IBM generator và không có planted
  patterns. E[singleton]=width/100; E[pair]=width(width−1)/(100·99), nên grid này
  chủ yếu minh họa F1 filtering/pair intersections, không stress deep patterns.

## Chạy lại

Cần Julia ≥1.9, Java ≥21, Python ≥3.11, curl. Controller chỉ dùng Python stdlib;
plotting dùng `requirements-plot.txt`. Từ root repo, sau khi activate venv nếu dùng:

```bash
julia --project=. -e 'using Pkg; Pkg.instantiate()'
python3 scripts/prepare_spmf.py --references
julia --project=. tests/runtests.jl
python3 tests/test_benchmark.py -v
python3 tests/smoke_benchmark.py
python3 scripts/acquire_benchmarks.py
julia --project=. scripts/benchmark_runner.jl --phase pilot --repeats 1 --output results/new-pilot
JULIA_NUM_THREADS=1 julia --project=. scripts/benchmark_runner.jl --output results/reproduced
python3 scripts/plot_results.py --results results/reproduced --report
```

Dùng output directory mới để giữ bằng chứng đã publish. `--resume` chỉ chấp nhận
checkpoint có cùng config, input, JAR, source hashes và runtime environment; cases đã xong không chạy lại.
Không dùng resume sau khi đổi mã/config. Có thể chạy riêng `--phase runtime`,
`--phase scalability`, `--phase length` với output riêng. Wrapper `.jl` tự truyền
Julia executable hiện tại; `PYTHON=/path/to/python` chọn interpreter phù hợp.

## Artifacts và giới hạn

`raw/benchmark_runs.csv`, `raw/summary.csv`, `raw/cases.json`, `raw/environment.json`,
`raw/protocol.json`; `correctness/comparisons.csv`; `plots/*.pdf,*.png`; các logs
stdout/stderr/command JSON và output-verification hash cho từng process. Full outputs,
subsets, synthetic và checkpoint giữ local (ignored); logs benchmark được đóng gói
archive để repo không có hàng nghìn file nhỏ. Extract bằng
`tar -xzf results/logs/benchmark-logs.tar.gz -C results/logs`.

Đọc phân tích trong Chương 2. Giới hạn: một máy, không core/frequency isolation,
fixed backend order, cache được làm ấm, 5 reps trong cùng phiên, Java heap cap 2 GiB,
không Java warm harness, chưa stress tới OOM/output explosion; không claim độ phức
tạp tuyến tính chỉ vì scalability plot. Adaptive tidsets, fused AND/popcount và
buffer pool là đề xuất tiếp, chưa nằm trong các số đo này.
