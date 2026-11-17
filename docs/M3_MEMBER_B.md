# Bàn giao Module 3 — Trần Thiên Phúc

Nhánh local feat/member-b-m3-delivery từ main e204a7f sau merge PR #4.
**Chưa push**. Core/schema và số liệu đo A giữ nguyên.

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
- Cold-run M3 Colab: đang kiểm bằng upload local; sẽ cập nhật khi hoàn tất.
  Không gọi M2 là M3, hoặc source bundle local là public main M3.

## Colab bản chưa push

Commit local rồi xuất bundle (có history để audit frozen source A):

~~~bash
git bundle create .tools/eclat-m3-source.bundle HEAD feat/member-b-m3-delivery
~~~

Mở Colab, upload notebooks/demo.ipynb, kết nối runtime mới; Files → Upload đưa
.tools/eclat-m3-source.bundle vào /content. Runtime → Run all.
Notebook ghi rõ dùng source local; tải datasets/SPMF và mine outputs mới.
Không đưa portable binaries/raw data/secrets vào bundle.
Sau publish M3 có thể chạy trực tiếp public main; cần kiểm link sau publish.
Hiện chưa tuyên bố public main đã chứa/chạy M3; không push để vượt yêu cầu của bạn.

## Nhóm cần xác nhận

A review PDF và tên/MSSV nếu yêu cầu, xác nhận gói 09/checklist và rà rubric.
Kiểm deadline Moodle/Group ID chính thức trước nộp URL repo public.
Review, publish và nộp bài không tự đánh dấu hoàn tất.
