# Kế hoạch nhóm: 3 tuần / 3 module / 2 thành viên

Nguồn nội bộ: `D:\Ke_hoach_Eclat_Julia_3_tuan_theo_module.pdf`, 3 trang.
Kế hoạch được dùng để tổ chức template theo yêu cầu trực tiếp của nhóm.
Các mốc bên dưới thuộc năm **2026**, múi giờ Asia/Saigon; không suy ra deadline Moodle.

## Phạm vi và cách phối hợp

A chuyên trách thuật toán/hiệu năng. B chuyên trách kiểm chứng/ứng dụng/Colab.
A hỗ trợ B sinh rules; B hỗ trợ A correctness và chuẩn hóa output. Mỗi module là
một gói 7 ngày, tự bố trí 3–4 buổi tập trung/tuần; không chia deadline từng ngày.
Sync 20–30 phút tại 03/11, 10/11, 17/11. Blocker lớn/API đổi báo ngay; blocker quá
24 giờ hoặc dự báo trễ milestone cần báo nhóm. PR khi phần code đủ ổn định để review.

Ưu tiên: đúng thuật toán → ứng dụng chạy thật → thực nghiệm → đóng gói. Viết báo cáo
ngay khi module có kết quả, không để toàn bộ đến tuần cuối.

## M1 · 28/10–03/11 · Foundation + Correctness

| Gói | Owner / reviewer | Đầu ra | Vị trí |
|---|---|---|---|
| 01 Paper, API và chuẩn I/O | A / B | Pseudocode DFS adaptation, threshold và output contract | docs/paper-notes.md, docs/API.md |
| 02 Eclat basic + parser + CLI | A / B | Vertical tid-list, DFS, output ổn định, CLI chạy | src/algorithm/baseline.jl, src/utils.jl, scripts/mine.jl |
| 03 SPMF oracle + ≥5 toy tests | B / A | Reference SPMF thật, comparator, edge tests, nguồn dữ liệu ứng dụng | tests/, data/toy/, data/manifest.csv |

**Gate M1:** Basic khớp 100% toàn bộ `(itemset, support)` với SPMF trên ≥5 CSDL,
CLI chạy, unit/edge tests pass; có mô tả Chương 1. Chưa đạt correctness thì chưa mở
tối ưu hoặc phân tích ứng dụng dựa trên output chưa đáng tin.

## M2 · 04/11–10/11 · Optimization + Applications

| Gói | Owner / reviewer | Đầu ra | Vị trí |
|---|---|---|---|
| 04 BitVector + benchmark harness | A / B | Backend cùng API, đối chiếu basic/SPMF, warm-up, pilot 4 datasets | src/algorithm/bitset.jl, scripts/benchmark_worker.jl, configs/experiments.toml |
| 05 Groceries + rules | B / A | Chuẩn hóa và mapping; top-10 theo lift; giải thích 3 luật | src/applications/groceries.jl, rules.jl, notebooks/demo.ipynb |
| 06 Splice DNA + kiểm chứng hai bản | B / A | 12 vị trí; EI/IE/N; bảng pattern 2–4 item; Colab tối thiểu | src/applications/dna.jl, notebooks/demo.ipynb |

**Gate M2:** Hai pipeline có dữ liệu và kết quả thật, tái lập được; BitVector khớp
basic/SPMF; Groceries đủ top-10 rules và diễn giải; DNA có support so sánh ba lớp;
Colab chạy tối thiểu. Không thay ứng dụng DNA bằng protein hoặc ảnh trong template này.

## M3 · 11/11–17/11 · Evaluation + Delivery

| Gói | Owner / reviewer | Đầu ra | Vị trí |
|---|---|---|---|
| 07 Bốn benchmark + biểu đồ + phân tích | A / B | Chess/Mushroom/Retail/T10I4D100K, 5–7 minsup/tập; runtime/output/RAM/scalability/transaction length | configs/, scripts/, results/ |
| 08 Báo cáo Chương 1–2 | A / B | Thuật toán, phương pháp đo, bảng/đồ thị, ≥2 hướng tối ưu tiếp | docs/latex/sections/ |
| 09 Chương 3 + Colab + README + final tests | B / A | Groceries/DNA, cold-run, nguồn, Report.pdf, public repo và notebook | docs/, notebooks/, README.md |

**Gate M3:** 4 benchmark đủ đồ thị; báo cáo IEEE tiếng Việt 10–15 trang, 3 chương;
full tests pass; public GitHub; public Colab cold-run thành công. B hỗ trợ đối chiếu
SPMF trên benchmark, rà số liệu và hình. A/B cùng rà PDF cuối.

Ngày **16–17/11** tập trung cold-run, sửa lỗi và đóng gói. Nếu M2 trễ, giảm phần
trình bày phụ và chọn minsup sau pilot để tránh bùng nổ output; vẫn giữ 2 ứng dụng
và 4 benchmark. Nếu hạn Moodle sớm hơn 17/11, rút ngắn M3 theo hạn chính thức.

## Quản lý công việc

Chín file trong [issues/](issues/) là issue briefs cục bộ, **chưa tạo GitHub Issues**.
Mã 01–09 là mã kế hoạch, không phải GitHub issue number. Điền tài khoản thật sau;
template không tự gửi tin Discord hoặc đăng nội dung lên GitHub.
