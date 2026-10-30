# Mẫu báo cáo IEEE tiếng Việt

`Report.tex` dùng `IEEEtran` chế độ conference, A4, hai cột. Nội dung đúng **3 chương**
thể hiện bằng `\section` theo định dạng IEEE. Chưa có Report.pdf; đây là mẫu soạn thảo,
không phải báo cáo hoàn chỉnh hoặc bằng chứng đủ 10–15 trang.

Dùng Overleaf có IEEEtran + Vietnamese fonts hoặc TeX Live với `IEEEtran`, `vntex`,
`babel-vietnamese`. Build từ thư mục này:

```text
pdflatex Report.tex
bibtex Report
pdflatex Report.tex
pdflatex Report.tex
```

Sau khi rà PDF, copy `Report.pdf` lên `docs/Report.pdf`. Đối chiếu định dạng với
[IEEE conference templates](https://www.ieee.org/conferences/publishing/templates).
Giữ font/cỡ chữ, lề và spacing của class; không thu nhỏ để nhét trang.

Gợi ý page budget: abstract + mở đầu trong Chương 1 khoảng 0.5–1 trang;
Chương 1 tổng 3–4 trang; Chương 2 khoảng 3–4 trang; Chương 3 khoảng 4–5 trang.
Tổng nội dung cần 10–15 trang, không tính references/phụ lục; cân theo kết quả thật.

A chủ trì Chương 1–2, B chủ trì Chương 3. Phần Chương 1 phát triển từ M1, phương
pháp/tối ưu và ứng dụng từ M2, số liệu và phân tích hoàn thiện M3. Mọi TODO phải được
thay bằng nội dung hiểu và kiểm chứng được. Figures vào `figures/`, caption và dẫn
chiếu trong lời văn; bảng/công thức dùng ký hiệu đã định nghĩa. Không dùng hình
placeholder như kết quả đo.

BibTeX có paper gốc và 3 nguồn khởi đầu khác (Apriori, SPMF, UCI). Đọc/kiểm lại
nguồn trước khi dùng, thêm nguồn Groceries đúng phiên bản thực tế. Lưu bản paper
tham khảo cục bộ tại `docs/references/` nếu cần; không tự coi PDF có quyền tái xuất bản.
