# Theo dõi review PR #4 — 17/11/2026

Nguồn: nhận xét [Hưng ngày 14/11](https://github.com/phuctran33/-DM-Eclat/pull/4#issuecomment-6875795804).

| Yêu cầu | Tình trạng | Bằng chứng |
|---|---|---|
| Đồng bộ README | Đã sửa mô tả Chương 3, mappings, pipeline/notebook và phạm vi log test | README phân biệt 787 checks M2 với 622 checks lịch sử A |
| Chạy Colab thật từ phiên sạch | Đã Run all: 7 cells, counts 1–7, 790 checks, 4 SPMF maps khớp | colab/2026-11-17-executed.ipynb, log và summary/hashes; M2-summary.json đã cập nhật true theo evidence |

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
Julia 1.12 cùng 1.9/1.11 để bảo vệ trường hợp này. Colab đã chạy lại từ phiên sạch và đạt; evidence pass được lưu tách biệt với log lỗi đầu.

## Bản sửa đã kiểm chứng

Code commit 07c0f28; [CI](https://github.com/phuctran33/-DM-Eclat/actions/runs/44057346550)
7/7 jobs pass, gồm Julia 1.9/1.11/1.12, ba controller OS và notebook sạch.
[Bằng chứng Colab thật](colab/README.md) có đủ 7 cells đúng source; không lỗi.
Không tự tick checklist review hoặc merge main. Build PDF cuối/rubric vẫn ở M3.
