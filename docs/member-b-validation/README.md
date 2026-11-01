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
