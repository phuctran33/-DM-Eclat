# Build báo cáo IEEE tiếng Việt

[Report.pdf](../Report.pdf) dùng IEEEtran conference A4, hai cột.
`Report.tex` nhập ba chương và các bảng trong `generated/`. Tám PDF hình lấy
trực tiếp từ [results/plots](../../results/plots/). Bảng ứng dụng lấy từ CSV
công bố.

Cần Python ≥3.11 và TeX Live với XeLaTeX, latexmk, IEEEtran, babel-vietnamese,
TeX Gyre, booktabs, placeins, algorithm và algpseudocode. Từ repo root:

```bash
python3 -m pip install -r requirements-report.txt
python3 scripts/application_tables.py --check
python3 scripts/build_report.py --latexmk latexmk
```

Script kiểm số trang, trích dẫn, font và tràn khung trước khi cập nhật PDF
và `docs/report-build.json`. Log và file build trung gian nằm trong
`.tools/report-build/`. Byte PDF có thể thay đổi theo thời điểm và engine.
Hồ sơ hash đi cùng PDF được phát hành. [Kiểm báo cáo](../RUBRIC_FINAL_AUDIT.md#bao-cao)
