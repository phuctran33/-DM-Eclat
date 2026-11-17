# Theo dõi review PR #4 — 17/11/2026

Nguồn: nhận xét [Hưng ngày 14/11](https://github.com/phuctran33/-DM-Eclat/pull/4#issuecomment-6875795804).

| Yêu cầu | Tình trạng | Bằng chứng |
|---|---|---|
| Đồng bộ README | Đã sửa mô tả Chương 3, mappings, pipeline/notebook và phạm vi log test | README phân biệt 787 checks M2 với 622 checks lịch sử A |
| Chạy Colab thật từ phiên sạch | Chờ đăng nhập Google trong phiên Colab riêng | Không dùng local/CI thay remote; M2-summary.json vẫn giữ false đến khi có output |

Giữ nguyên core, schema, dữ liệu và kết quả đã review. Build PDF cuối/cân trang/rà
rubric thuộc M3. Checklist 05/06 vẫn để reviewer xác nhận sau khi có đủ bằng chứng.

## Lỗi phát hiện trên Colab thực

Colab dùng Julia 1.12.6/Python 3.13.18. Cell test phát hiện runner dùng `root` của
input fixture để walkdir tìm mã nguồn (`/tmp/.../src` không tồn tại), thay vì
repository chứa code đang chạy. Đã dùng APPLICATION_ROOT riêng cho code hashes,
giữ root làm input root; thêm ba regression checks (tổng 790). Không sửa core
Eclat/rules hoặc schema. Hai pipeline chạy lại và SPMF đạt; toàn bộ 18 output
hashes giống kết quả trước. Metadata run.toml/validation được tạo lại bằng code
đã sửa. Notebook hiện in stdout/stderr thật trước khi báo lỗi subprocess. CI thêm
Julia 1.12 cùng 1.9/1.11 để bảo vệ trường hợp này. Colab sẽ được chạy lại từ phiên sạch.
