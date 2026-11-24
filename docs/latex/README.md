# Build báo cáo IEEE tiếng Việt

[Report.pdf](../Report.pdf) có 10 trang nội dung và 1 trang tài liệu tham khảo
với 11 nguồn. Report dùng IEEEtran conference A4, hai cột và font TeX Gyre.
Chương 1–2 dùng dữ liệu đo của A. Bảng Chương 3 lấy CSV Groceries/Splice của B.

Từ repo root, cài Python 3.11+, TeX Live với XeLaTeX, latexmk, IEEEtran,
babel-vietnamese, TeX Gyre, booktabs, placeins, algorithm và algpseudocode. Sau đó chạy:

```bash
python3 -m pip install -r requirements-report.txt
python3 scripts/application_tables.py --check
python3 scripts/build_report.py --latexmk latexmk
```

Có thể chọn [Tectonic 0.17.0](https://github.com/tectonic-typesetting/tectonic/releases/tag/tectonic%400.17.0)
bằng `--tectonic /đường/dẫn/tectonic`. Lần đầu có thể cần tải TeX bundle.
Hình và bảng đã commit đủ để build từ clone sạch. Khi cập nhật bảng ứng
dụng có chủ đích, chạy `python3 scripts/application_tables.py`, xem diff rồi
build lại. Tái render benchmark sẽ tạo artifacts mới, nên dùng output riêng.

Script giữ console log và `Report.log` ở thư mục riêng trong
`.tools/report-build/`. Kiểm final log, số trang, ký tự và source hashes trước
khi cập nhật `docs/Report.pdf` cùng `docs/report-build.json`.
Mã nguồn, timestamp và engine có thể làm byte PDF thay đổi giữa các lần build.
Phát hành một PDF cùng metadata tương ứng.

Bản cuối được build bằng Tectonic 0.17.0 và được kiểm trực quan sau khi build.
[Đối chiếu báo cáo](../RUBRIC_FINAL_AUDIT.md#bao-cao). Bản B cho phiên Colab
bundle dùng Tectonic, có [PDF ở commit lịch sử](https://github.com/phuctran33/-DM-Eclat/blob/392d165b897eea7c78d9ce2076b5e05ac0c0e7c7/docs/Report.pdf)
và [log build cũ](../member-b-validation/m3/report-build.log).
`MemberAReview.tex` là entry point để xem riêng Chương 1–2.
