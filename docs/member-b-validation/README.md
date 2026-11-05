# Kiểm chứng B — 01/11/2026

- unit-tests.log: 206 Julia checks pass, 0 fail/error/skip trong suite B độc lập.
- source-tests.log: 4 Python acquisition/adapter tests pass, không cần mạng.
- preparation-report.json: kiểm chéo mọi dòng dữ liệu thật với oracle Python,
  hai lần export giống byte, overwrite guard và diagnostic comparison.
- spmf/: stdout/stderr và summary cho 5 SPMF runs thật, khớp vét cạn.
- clean-source-*.log/source-isolation.json: chạy suite và tái tạo dữ liệu trong source copy mới.
- notebook-local.log/json: tất cả 7 code cells thực thi local, mining tắt.
- environment.json: runtime/source hashes dùng khi kiểm chứng (không phải benchmark).

Dữ liệu: Groceries 9.835 giỏ/169 items; Splice raw 3.190, giữ 3.185, mapping 48 IDs.
Các candidates so sánh DNA trong integration audit được chọn thủ công để test,
không được gọi là Eclat output/kết quả ứng dụng cuối. Miner main vẫn TODO.
Remote CI/Colab chưa được xác nhận bằng log này. Xem HANDOFF_MEMBER_B.md để chạy lại.


Reference SPMF canonical LF đã được test qua Git snapshot, tránh lệch checksum
sau clone trên Windows/Linux. Summary giữ cả raw/canonical hashes. Log project
initial là lịch sử trước 5 regression checks LF; unit-tests.log/clean-source-tests.log
là kết quả cuối **206** checks. PDF report chưa build vì máy chưa có LaTeX;
phần tiền xử lý Chương 3 đã điền số liệu và kiểm các citation keys.

## Tích hợp main đã duyệt — 05/11/2026

A đã vào main qua PR #1 (`b821235`). Conflict PR #3 được xử lý bằng cách giữ
implementation A, preparation/export B, provenance từng bên và CI chung.

- integration-main.log: full suite A+B **762 pass**, 4 Python source tests pass;
  controller Windows **9 pass/1 skip** vì phép đo POSIX; artifact audit đạt.
- integration-main-notebook.log: cả 7 code cells thực thi local, preparation và
  list/bitset bật; dữ liệu thật/audit và hai toy CLI đối chiếu SPMF đạt.
- Tất cả 6 dòng nguồn A/B và hashes artifacts A được bảo toàn.

Các log 01/11 vẫn là lịch sử kiểm chứng riêng B. Chưa chạy lại full benchmark,
remote Colab hoặc tạo kết quả ứng dụng mined cuối trong lần xử lý conflict này.
