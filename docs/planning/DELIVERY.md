# Checklist nghiệm thu và bàn giao

Các mục hoàn thành có bằng chứng trong [rubric audit](../RUBRIC_FINAL_AUDIT.md).
Mốc Module 1–3 là lịch nội bộ.

## Thuật toán và kiểm chứng

- [x] Basic/BitVector dùng vertical tidsets, xuất đủ frequent itemsets và support.
- [x] CLI hai dạng threshold và I/O SPMF. Kiểm cả trường hợp output alias của input.
- [x] Vét cạn, edge, randomized, word tails và năm toy databases khớp Java SPMF.
- [x] Lệnh `julia --project test/runtests.jl` và lệnh trực tiếp ở `tests/` chạy cùng bộ test.
- [x] Hai pipelines ứng dụng dùng miner, kiểm labels/rules/counts và SPMF.

## Thực nghiệm và báo cáo

- [x] 4 benchmarks, 6 ngưỡng/tập, exact support maps và 46 hashes evidence.
- [x] Runtime, output size, peak RSS, Retail subsets và synthetic width plots. Các
  mức độ rộng dùng chung hoán vị theo dòng. Phân tích Retail tách xu hướng
  của Basic và BitVector.
- [x] Giải thích giới hạn đo và ít nhất hai tối ưu tiếp.
- [x] Groceries top-10 theo lift, ba diễn giải và số giỏ phân biệt. Splice có counts
  đếm lại theo lớp, giải thích tọa độ ở lớp N và ZIP UCI dự phòng đã kiểm hash.
- [x] Gate nghiệm thu yêu cầu đúng một đối chiếu SPMF cho từng đầu vào ứng dụng.
- [x] IEEE 10 trang nội dung, 11 nguồn, đã kiểm bố cục mọi trang và hash nguồn.
- [x] README có các lệnh tái lập, test stdout, nguồn, PDF và link Colab.

## Nghiệm thu trước nộp

- [x] Chạy notebook local từ mã tích hợp và kiểm toàn bộ artifacts mới.
- [x] Giữ bằng chứng Colab thật dùng Git bundle M3 ngày 17/11.
- [ ] Xác nhận **Runtime → Run all** từ public main trong runtime Colab mới.
  Lưu commit, output đủ 7 cells, versions, dataset hashes và final gate.
- [ ] Xác nhận với giảng viên việc dùng URL FIMI pin hash cho bốn tập dưới 4 MiB.
  Nếu cần HF/Kaggle, đối chiếu hash bản có quyền tái phân phối trước khi cập nhật
  nguồn. [Phân tích hosting](../RUBRIC_FINAL_AUDIT.md#dataset-hosting).
- [ ] Gửi bản thảo/bản cuối cho bên cung cấp Retail theo điều kiện nguồn.
- [ ] Hai thành viên luyện vấn đáp, xác nhận thông tin nhóm và hạn Moodle.
- [ ] Nộp một URL GitHub công khai qua Moodle.

[Chuẩn bị vấn đáp](../DEFENSE_GUIDE.md) · [Điều kiện dữ liệu Retail](https://www.cs.rpi.edu/~zaki/Workshops/FIMI/data/retail.pdf)

<a id="colab-public-main"></a>
## Lưu bằng chứng từ Colab public main

1. Mở notebook từ đường dẫn công khai trong runtime CPU mới. Giữ `RUN_BENCHMARKS=False`
   và chọn **Runtime → Run all**. [Notebook public](https://colab.research.google.com/github/phuctran33/-DM-Eclat/blob/main/notebooks/demo.ipynb).
2. Đối chiếu `SOURCE COMMIT` ở cell đầu với HEAD của `main` được nghiệm thu.
   Cần đủ 7 code cells, 792 Julia checks, bốn đối chiếu SPMF ứng dụng, bốn
   đối chiếu benchmark live và `PASS final delivery`.
3. Tải notebook đã chạy **có outputs** qua **File → Download → Download .ipynb**.
   Tải `delivery-validation.json` ở đường dẫn in cuối notebook. Giữ log của
   bảy cells nếu tách riêng, gồm source commit, versions và dataset hashes.
   Đóng mục Colab sau khi kiểm các file này và thấy `runtime: google-colab`.
