# Colab Run all thực — 17/11/2026

Đã chạy notebook trên **Google Colab / Google Compute Engine**, không phải
local hoặc CI được gán nhãn Colab. Notebook tại source commit
`07c0f2864a4621d16e1630f91d0f6da61dad5de4`, Julia **1.12.6**.
Trước Run all, trình duyệt hiển thị kết nối runtime mới và cả 7 execution counts
đều rỗng. Sau chạy, 7 code cells có counts **1,2,3,4,5,6,7**, không error outputs.

- [Notebook có output](2026-11-17-executed.ipynb): tải trực tiếp bằng menu Colab;
  đối chiếu từng code cell với source commit, không chèn candidates hoặc sửa output.
- [Log đầy đủ](2026-11-17-run-all.log): xuất stream/text outputs của 7 cells.
- [Summary/hashes](2026-11-17-summary.json): nguồn commit, URL Colab, thời gian UTC,
  hashes notebook/log và từng code cell; tài khoản Google không được đưa vào evidence.

Kết quả: **790 Julia checks pass**, Groceries 1.001 patterns/22 rules/top-10;
DNA EI/IE/N 381/209/48 patterns, 463 comparison rows. Bốn live Java SPMF maps
khớp 100%. Notebook capture đã kiểm đủ số thứ tự cell, đúng source, không lỗi,
tổng checks và cả bốn marker SPMF trước khi đặt remote_colab_executed=true.

Notebook đã tải chỉ được chuẩn hóa định dạng JSON và bỏ metadata attribution
tài khoản Google nếu có; code, execution counts và output được giữ nguyên.
SHA-256 download gốc và bản evidence đều ghi trong summary.

`RUN_BENCHMARKS`/`FINAL_DELIVERY_VALIDATION` vẫn false theo phạm vi M2. Dòng cuối
nhắc nghiệm thu cuối/Colab cold-run là nhánh kiểm **M3**, không phủ nhận lần Run all
M2 đã lưu ở đây. Build PDF/cân trang/rà rubric và final validation M3 là việc riêng.
Checklist 05/06 vẫn do reviewer xác nhận, không tự tick chỉ từ việc có evidence.
