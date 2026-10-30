# Dữ liệu ứng dụng — B / M1–2

- Groceries: adapter raw→canonical `groceries.csv`, header `basket_id,item_name`, mapping và transactions chuẩn.
- UCI Splice: `splice.data`, metadata/sample ID, class EI/IE/N, mapping position/base,
  transactions tổng và theo lớp; cửa sổ đã khóa 25:36, ambiguity trong window bị loại.

Không có dữ liệu thật trong template. Ghi nguồn/license/version/hash vào manifest.
Mã chuẩn bị nằm trong `src/applications/` và được gọi từ Colab notebook.
Áp dụng `docs/SCHEMA.md` và `schemas/contracts.toml`; không nhầm nhãn lớp N với base ambiguity N.
