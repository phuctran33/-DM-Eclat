# Báo cáo IEEE tiếng Việt

Chương 1–2 của Member A có implementation, protocol, kết quả thật và phân tích.
Chương 3 giữ nguyên nội dung template thuộc B; chưa có kết quả hai ứng dụng.
Không coi bản PDF review này là nghiệm thu 10–15 trang cuối của cả nhóm.

Cần TeX Live/Overleaf có IEEEtran, vntex, babel-vietnamese, amsmath, booktabs,
algorithm và algpseudocode. Trước build, sinh figures/tables từ CSV thực:

```bash
python3 scripts/plot_results.py --results results --report
cd docs/latex
latexmk -pdf -interaction=nonstopmode -halt-on-error MemberAReview.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error Report.tex
```

Chạy lệnh đầu từ repo root. Bản `MemberAReview.pdf` chỉ gồm Chương 1–2, copy đã
kiểm tra ở `docs/Member-A-review.pdf`. `Report.pdf` local vẫn gồm ba chương,
Chương 3 pending có nhãn rõ. Không ghi lên `docs/Report.pdf` cuối trước khi B hoàn
thiện ứng dụng và nhóm review. Khi latexmk không có, dùng pdflatex → bibtex →
pdflatex → pdflatex cho mỗi entry point.

Hình ở `figures/`, fragments bảng ở `generated/`, nguồn CSV/logs trong `results/`.
Các hình có caption/label/reference và units; code sinh hình cũng copy PDFs để
clean clone build được review mà không phải chạy lại benchmark. Không sinh bảng
bằng số liệu tự điền. Các warnings reference/citation phải hết sau các pass cuối;
underfull boxes do căn cột tiếng Việt có thể còn, không đồng nghĩa lỗi biên dịch.

Giữ font/lề/spacing IEEEtran. A dùng khoảng 3 trang cho implementation và phần
còn lại cho phương pháp/kết quả; B cân dung lượng Chương 3 để bản nhóm đạt 10–15
trang nội dung, chưa tính tài liệu tham khảo. Abstract ghi rõ tình trạng bản review;
không đưa kết quả ứng dụng chưa chạy vào abstract/kết luận.
