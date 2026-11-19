# Google Colab cold-run M3 — 17/11/2026

**Đã chạy thật, pass 7/7 code cells**, execution counts 1–7, không error.
Julia 1.12.6, Java 21, SPMF 2.64b kiểm JAR hash.
790 Julia checks + 4 Python source tests + 6 delivery-gate tests.
Bốn ứng dụng (Groceries/EI/IE/N) và bốn benchmark (Chess/Mushroom/Retail/T10I4D100K)
đều khớp toàn bộ maps với Java SPMF. Final delivery gate pass:
PDF hash hiện hành, 10 trang nội dung, 22 rules, 463 DNA candidates,
70 full-map comparisons lưu trữ của A được audit.

## Nguồn và phạm vi bằng chứng

Source **ee2d46d69d7b4925d3742378c9ee3b16a13af54c**, upload Git bundle vào
VM sạch qua Files. Trước Run all có đúng 7 cells chưa chạy; /content chỉ có
sample_data và source bundle. Datasets/SPMF được tải có kiểm hash; outputs ứng dụng
và benchmark được mine mới. Chỉ kiểm correctness, không đo lại runtime/RSS của A.

Đây là **source local chạy trên Google Colab**, chưa push GitHub theo yêu cầu.
Không gọi phiên này là public main M3 đã chạy. Sau publish, nhóm kiểm lại URL
public main. Bằng chứng public M2 giữ riêng ở ../../colab/.

Lần thử đầu chưa nhận source bundle được dừng, xóa VM và xóa output. Bằng chứng
ở đây chỉ ghi lần chạy sạch sau khi bundle đã có trong /content; không ghép output
từ các lần thử. Bảy code cells được so đúng từng ký tự với notebook ở commit nguồn.

## Files

- 2026-11-17-executed.ipynb: tải trực tiếp từ Colab, giữ source/output; chỉ bỏ
  metadata browser/account/runtime session.
- 2026-11-17-run-all.log: text output của cả bảy code cells.
- 2026-11-17-summary.json: commit/bundle/hash download, hash artifacts, counts,
  before-run state và final delivery JSON. public_github_m3_executed vẫn false.

Đã kiểm: 7 code cells đúng nguồn, execution 1–7; không output_type=error;
cộng các Julia test tables = 790; bốn SPMF PASS ứng dụng và bốn full-map benchmark;
runtime final gate là google-colab; hash PDF trong output bằng docs/Report.pdf.
