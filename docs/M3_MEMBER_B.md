# Bàn giao Module 3 — Trần Thiên Phúc

Ghi nhận lịch sử của bản PR #5 trước tích hợp. [Trạng thái hiện tại](planning/STATUS.md) · [Rubric audit](RUBRIC_FINAL_AUDIT.md). PDF và metadata của phiên này nằm ở [snapshot 392d165](https://github.com/phuctran33/-DM-Eclat/tree/392d165b897eea7c78d9ce2076b5e05ac0c0e7c7/docs).

Nhánh PR feat/member-b-m3-delivery từ main e204a7f sau merge PR #4.
Chờ review/merge M3 vào main. Core/schema và số liệu đo A giữ nguyên.

## Đã hoàn thành

1. Report.pdf IEEE A4 tiếng Việt, đủ ba chương; 10 trang nội dung + 1 bibliography,
   10 nguồn. Chương 3 cập nhật Colab thật M2, top-10/ba diễn giải Groceries,
   patterns DNA 2–4 item và giới hạn. Bảng sinh từ CSV, không điền số tay.
2. Build Tectonic 0.17.0, kiểm số trang/glyph/citation/ref/tràn cột, hash PDF/nguồn;
   đã render/rà trực quan.
3. Audit A: 46 artifact hashes, 35 cases/875 measurements/70 full-map comparisons,
   aggregates và OS logs khớp source đo 49dafc999b6c00f8c4275ee68f99d4a6e3046f3d.
4. Live correctness thêm tại memory_minsup: Chess 0.85 → 2.669 patterns;
   Mushroom 0.50 → 153; Retail 0.03 → 32; T10I4D100K 0.01 → 385.
   List/BitVector/SPMF khớp toàn map. Không gọi đây là đo lại 35 cases/runtime/RSS.
5. Notebook mặc định review benchmark + gate trên output ứng dụng mine mới.
   Local 7/7 cells; 790 Julia checks, 4 source tests, 6 delivery tests,
   bốn ứng dụng live SPMF pass. Gate không yêu cầu đo lại benchmark trên Windows.
6. Acquisition giữ POSIX paths/thứ tự manifest trên mọi OS; README/CI đồng bộ M3.

## Chạy và bằng chứng

~~~powershell
python -B scripts/run_notebook.py
~~~

Kernel Python 3.11+ (máy này: Eclat (Python 3.11)); notebook gọi Julia.
Mỗi lần tạo output mới .tools/notebook-runs. Gate từ chối dùng results/applications
đã ship thay mining mới. Các lệnh rời và build có trong README.

- docs/Report.pdf, docs/report-build.json, docs/member-b-validation/m3/report-build.log.
- docs/member-b-validation/m3/local-run-all.log, local-summary.json.
- docs/member-b-validation/m3/benchmarks/: maps/stdout/stderr/review.json thật của B.
- docs/member-b-validation/colab/: bằng chứng public M2 giữ nguyên.
- [Cold-run M3 Colab](member-b-validation/m3/colab/README.md): **7/7 cells pass**,
  source ee2d46d upload từ Git bundle vào VM sạch; Julia 1.12.6, 790 checks,
  bốn ứng dụng + bốn benchmark SPMF pass, final PDF/data gate pass.
  Có notebook output/log/summary đã kiểm source từng cell và execution 1–7.
  Đây là bản local chạy trên Colab; public main M3 vẫn chờ merge.

## Cách kiểm source trước khi merge

Commit local rồi xuất bundle (có history để audit frozen source A):

~~~bash
git bundle create .tools/eclat-m3-source.bundle HEAD feat/member-b-m3-delivery
~~~

Mở Colab, upload notebooks/demo.ipynb, kết nối runtime mới; Files → Upload đưa
.tools/eclat-m3-source.bundle vào /content. Runtime → Run all.
Notebook ghi rõ dùng source local; tải datasets/SPMF và mine outputs mới.
Không đưa portable binaries/raw data/secrets vào bundle.
Sau merge M3 có thể chạy trực tiếp public main; cần kiểm lại link sau merge.
Phiên Colab đã lưu dùng bundle source ee2d46d; chưa tuyên bố public main đã chạy M3.

## Nhóm cần xác nhận

A review PDF và tên/MSSV nếu yêu cầu, xác nhận gói 09/checklist và rà rubric.
Kiểm deadline Moodle/Group ID chính thức trước nộp URL repo public.
Review, publish và nộp bài không tự đánh dấu hoàn tất.

## Provenance local và Colab

Local run được thực hiện trước commit M3: review.json ghi HEAD tại thời điểm chạy
và source_sha256 của cây mã thực tế. Colab clone commit ee2d46d từ bundle;
bằng chứng remote là source đã commit. Các cập nhật sau cold-run chỉ đồng bộ
tài liệu/evidence, giữ nguyên code notebook/Julia/PDF đã kiểm.
Raw outputs SPMF giữ native line endings bằng gitattributes để hash đúng khi checkout
Windows/Linux; đã kiểm cả Git blobs so với artifact_sha256 trong review.json.

## Phần còn chờ review/merge

Đã xong triển khai/kiểm thử của B. Chờ A review PDF/gói 09.
CI M3 được kích hoạt khi push/PR; trạng thái đọc từ GitHub Actions, không suy từ local tests.
Kiểm lại public main Colab sau merge. Không tự xác nhận reviewer hoặc nộp Moodle.
