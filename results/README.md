# Bằng chứng thực nghiệm Member A

- `raw/dataset_statistics.csv`, `dataset_provenance.json`: tính trên file đã tải/chuẩn hóa.
- `raw/benchmark_runs.csv`: raw repetitions theo shared schema v1.0.0.
- `raw/summary.csv`: median/min/max, số ok/timeout/oom/error, output và peak RSS.
- `raw/environment.json`, `protocol.json`, `cases.json`: versions/source/config/input hashes.
- `correctness/comparisons.csv`: so toàn bộ maps với SPMF, không chỉ output count.
- `raw/optimization.csv`, `memory_comparison.csv`, `end_to_end_medium.csv`: bảng dẫn xuất thật.
- `plots/*.pdf,*.png`: hình từ raw/summary CSV, không có số liệu dựng tay.
- `logs/final-tests.log`, `controller-tests.log`, `benchmark-smoke.log`: kiểm thử thực.
- `logs/benchmark-logs.tar.gz`: stdout/stderr/command/status và output-verification hashes.
- `reference/`: logs/version/provenance của năm SPMF references.

Extract archive: `tar -xzf results/logs/benchmark-logs.tar.gz -C results/logs`.
Full pattern outputs, subsets, synthetic data và checkpoint giữ local, ignored;
regenerate bằng runner. Không commit JAR, raw benchmarks hoặc cache runtime.

Đọc `docs/experiments.md` về hai phạm vi timer, OS peak RSS, timeout, warm-up,
spread và hạn chế. Tạo lần đo mới bằng `--output results/reproduced`; không trộn số
đo của hai machines/protocols vào một bảng. Ứng dụng Groceries/DNA chưa có kết quả.
