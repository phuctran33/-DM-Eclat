# Nhật ký kiểm chứng Member A

Ngày: **31/10/2026**, Asia/Saigon. Workspace được clone sạch từ
`phuctran33/-DM-Eclat`, base `e1c9865`. Branch `feat/member-a-eclat-complete`.
Core/benchmark code cho phép đo có commit trong `results/raw/environment.json`;
final feature HEAD đọc bằng `git rev-parse HEAD` để tránh ghi hash tự tham chiếu.

## Trạng thái ban đầu thực sự

Julia chưa có trong PATH. Cài local Julia **1.10.10 arm64** từ binary chính thức,
SHA-256 archive đối chiếu checksum của julialang.org:
`52d3f82c50d9402e42298b52edc3d36e0f73e59f81fc8609d22fa094fbad18be`.
Runtime ở `.tools/julia-1.10.10/bin/julia`, ignored; không thay đổi shell profile.
Java 23.0.1, Python 3.14.0, TeX Live 2025/pdflatex/latexmk đã có trên máy.

`Pkg.instantiate()` chạy thật, tạo Manifest stdlib. Test scaffold ban đầu:
66 pass, 2 Broken/skip. Khi bật miner, suite lỗi ở baseline TODO như dự kiến;
không gọi scaffold pass là correctness. Logs `initial-instantiate.log`,
`initial-tests.log`, `initial-miner.log`. SPMF latest không đọc được bởi Java 23;
chuyển sang archive chính thức 2.64b (class version 65/Java ≥21), pin hash.

## Kiểm thử Julia cuối

```bash
ECLAT_TEST_MINER=1 ECLAT_TEST_SPMF=1 ECLAT_TEST_BACKENDS=list,bitset \
  julia --project=. tests/runtests.jl
```

| Testset | Pass |
|---|---:|
| SPMF I/O and canonical comparison | 14 |
| Threshold boundaries and API validation | 19 |
| Shared schema v1 | 33 |
| Edge cases, input ownership and packed-word boundaries | 267 |
| Eclat: five different databases, selected backends | 80 |
| Randomized oracle and transaction-order invariance | 80 |
| Association rules and PreparedDataset integration | 94 |
| CLI round trip and failure paths | 10 |
| Exact agreement with SPMF on five databases | 25 |
| **Tổng** | **622** |

Stdout thực tế: `results/logs/final-tests.log`. Không có fail/error/Broken/skip trong
lần full suite này. Mặc định tests cũng bật mining/SPMF và cả hai backends.
Một CSDL rỗng, transaction rỗng trong RAM, repeated rows, non-contiguous IDs,
strict invalid input, min_count=1/n/n+1, caller non-mutation và word tails đều có
checks. Oracle exhaustive không dùng helper intersection của miner.

## Oracle SPMF và integration

`python3 scripts/prepare_spmf.py --references` tạo thật 5 references 40%.
Manifest đúng schema v1.0.0: input/output/JAR hashes, versions, command/status.
Năm fixture counts: basic=7, dense=14, sparse=0, duplicates=5, boundary=4.
List và BitVector so **toàn bộ map** với references, không chỉ count; sparse=0
được ghi rõ. CLI relative/count/bitset cho byte output giống nhau và comparator
exit 0. Các trường hợp invalid CLI không ghi đè input.

`python3 tests/test_benchmark.py -v`: 5 unittest methods, 0 fail/skip. Bao gồm
process thật, OS RSS, timeout/error, logs phân biệt decimal run IDs, strict maps,
SPMF count bins, reference hashes và failure-aware aggregation. Log
`results/logs/controller-tests.log`.

`python3 tests/smoke_benchmark.py`: grid toy thật có 5 measurements thuộc hai scopes,
2 full-map comparisons; resume không nhân đôi dữ liệu; thay runtime signature bị
từ chối; synthetic byte-deterministic và Retail-style subsets nested. Log
`results/logs/benchmark-smoke.log`. Không diễn giải các số timing smoke thành
kết quả benchmark chính thức.

Trong pilot đầu, phát hiện Path.with_suffix làm mất suffix tên log chứa decimal
minsup; đã sửa thành append extension, thêm kiểm tra log isolation và chạy lại
pilot verified. Dữ liệu chính thức dùng tên log đã sửa. Sau khi bắt đầu đợt đo, chỉ sửa định
dạng bảng/hình và tăng guard resume chống trộn runtime; bổ sung kiểm tra scientific-notation minconf trong helper rules (không được gọi
trong mining benchmark); không đổi miner, vùng
@timed hay OS monitor của đợt đo đã lưu. Mã nguồn phép đo được pin riêng.

## Kiểm chứng thí nghiệm và report

Bằng chứng chính: `results/raw/benchmark_runs.csv`, `summary.csv`,
`correctness/comparisons.csv`, environment/protocol/cases và logs archive.
Figures/tables từ các CSV này, không từ pilot 1 repetition hoặc số liệu mẫu.
Scripts không truncate output; từng repetition được kiểm lại full-map.

`schemas/contracts.toml`, shared structures và `src/schemas.jl` giữ nguyên so với
base; chỉ cập nhật trạng thái trong tài liệu schema. B không bị đổi mapping/labels.
Association-rule helper được kiểm bằng PreparedDataset fixture, không gọi đó là
Groceries/DNA chạy thực. Notebook chỉ sửa các tế bào A/API/SPMF/benchmark; cells
ứng dụng B giữ TODO và cờ false. Local notebook run không phải Colab cold-run.

Build LaTeX: `latexmk -pdf -interaction=nonstopmode -halt-on-error` cho cả
`MemberAReview.tex` và `Report.tex`. PDF review A được lưu riêng, không tạo
`docs/Report.pdf` cuối với nội dung Chương 3 chưa hoàn thành. Log và kết quả audit
cuối được đính kèm cùng artifacts. B cần review nội dung/paper adaptation và hoàn
thiện Chương 3, Colab, thông tin nhóm/đầu ra ứng dụng trước nghiệm thu toàn nhóm.
