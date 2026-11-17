# Báo cáo IEEE tiếng Việt

[Report.pdf](../Report.pdf): **10 trang nội dung + 1 trang tài liệu tham khảo**,
ba chương, 10 nguồn. Chương 1–2 giữ số liệu A; Chương 3 có Groceries/DNA mined thật.

Từ repo root, Python 3.11+:

~~~bash
python -m pip install -r requirements-report.txt
python scripts/application_tables.py --check
python scripts/build_report.py --tectonic /path/to/tectonic
~~~

Máy này dùng .tools/tectonic/tectonic.exe, **Tectonic 0.17.0**;
cache .tools/tectonic-cache. [Release chính thức](https://github.com/tectonic-typesetting/tectonic/releases/tag/tectonic%400.17.0),
asset tectonic-0.17.0-x86_64-pc-windows-msvc.zip, SHA-256:
f61ce51f0b0ade1015b7de7ef368541c5424e9756ecbd0d7af97d6d48030845f.
Không commit compiler/cache. Build đầu cần mạng tải TeX bundle/font.
TeX Gyre Termes/Cursor/Heros có đủ glyph tiếng Việt, giữ IEEEtran A4.

Build chạy đủ TeX/BibTeX passes, kiểm PDF bằng pypdf rồi mới copy docs/Report.pdf.
docs/report-build.json ghi PDF/source hashes; sửa nguồn cần build lại.
Log: docs/member-b-validation/m3/report-build.log.
Không unresolved refs/citations, thiếu glyph nội dung hoặc overfull boxes;
đã render/rà trang đầu, bảng ứng dụng và bibliography.
Một số underfull boxes tiếng Việt/URL còn tồn tại; Tectonic cảnh báo encoding
comment algorithm.sty và Fontconfig Windows, nhưng OTF resolve/nhúng đúng.
Không gọi các cảnh báo này là thiếu ký tự trong PDF.

Nguồn hỗ trợ thêm pdfLaTeX + BibTeX trên TeX Live/Overleaf với IEEEtran, vntex,
babel-vietnamese, amsmath, booktabs và algorithm/algpseudocode:

~~~bash
cd docs/latex
latexmk -pdf -interaction=nonstopmode -halt-on-error Report.tex
~~~

Engine khác cần rà lại PDF/số trang; metadata bản phát hành do script build tạo.
MemberAReview.tex là entry point review lịch sử, không thay PDF đủ ba chương.
Bảng ứng dụng sinh từ CSV qua scripts/application_tables.py; các hình/bảng A
đã render, không cần tạo lại để build PDF và làm đổi hash evidence đã đo.
