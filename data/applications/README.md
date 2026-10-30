# Dữ liệu ứng dụng — B / M1–2

- Groceries: raw file theo snapshot đã chốt, mapping ID↔product name, transactions chuẩn.
- UCI Splice: `splice.data`, metadata/sample ID, class EI/IE/N, mapping position/base,
  transactions tổng và theo lớp; xác nhận cửa sổ 12 vị trí.

Không có dữ liệu thật trong template. Ghi nguồn/license/version/hash vào manifest.
Mã chuẩn bị nằm trong `src/applications/` và được gọi từ Colab notebook.
Xem `docs/applications.md` để tránh nhầm nhãn lớp N với base ambiguity N.
