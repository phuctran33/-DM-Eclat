# Ma trận yêu cầu đề ↔ template ↔ module

Nguồn: [HCMUS FIM](https://hcmus-cs-ta.github.io/lab-book/data-mining/projects/itemset/),
đọc ngày 30/10/2026. Nội dung dưới đây diễn giải yêu cầu để nhóm kiểm tra;
không thay thế thông báo giảng viên hoặc Moodle.

| Yêu cầu | Nơi thực hiện / bằng chứng | Owner / module |
|---|---|---|
| Một thuật toán, tự cài đặt từ original paper | Zaki 2000; docs/paper-notes.md, src/algorithm/ | A+B / M1 |
| Julia ≥1.9, dùng kiểu dữ liệu phù hợp ngôn ngữ | Project.toml, typed atoms, multiple dispatch, BitVector | A / M1–2 |
| Xuất mọi frequent itemset và support | mine API và CLI SPMF | A / M1 |
| Khớp đầy đủ SPMF trên ≥5 CSDL, test tự động | tests/test_correctness.jl, test_spmf.jl, comparator | B / M1 |
| ≥1 tối ưu có đo thời gian/bộ nhớ so với basic | BitVector; worker + external RSS | A / M2–3 |
| ≥4 benchmark cộng đồng FIM | Chess, Mushroom, Retail, T10I4D100K | A; B kiểm chứng / M3 |
| Correctness trên từng benchmark | Cùng file/threshold, canonical maps, không chỉ count | B / M3 |
| Runtime theo 5–7 minsup/tập, so SPMF cùng biểu đồ | configs/experiments.toml, CSV và plots | A / M3 |
| Output size theo minsup | Đếm đủ itemset, phân tích dense/sparse | A / M3 |
| Peak RAM tại minsup trung bình | Cùng metric RSS basic/bitset; phân biệt allocations | A / M3 |
| Scalability 10%,25%,50%,75%,100% | Retail, nested seeded samples | A / M3 |
| Ảnh hưởng độ dài giao dịch nếu liên quan | Synthetic với n/m/minsup cố định, width thay đổi | A / M3 |
| Giải thích theo paper/complexity, ≥2 tối ưu tiếp | Chương 1–2 | A / M3 |
| Ứng dụng 1: chọn basket hoặc event log | Nhóm chọn Groceries, top-10 rules theo lift | B; A hỗ trợ rules / M2–3 |
| Ứng dụng 2: chọn sinh học hoặc hình ảnh | Nhóm chọn UCI Splice DNA, EI/IE/N | B / M2–3 |
| Hai ứng dụng dùng chính cài đặt nhóm | Notebook import src/ và chạy pipeline thật | A+B / M2–3 |
| Seed cố định, dữ liệu và kết quả tái lập | Seed 42, manifest, config, cold-run | A+B / xuyên suốt |
| Notebook Colab có code chuẩn bị dữ liệu | notebooks/demo.ipynb và helpers src/applications/ | B / M2–3 |
| Báo cáo tiếng Việt, IEEE 10–15 trang | docs/latex/Report.tex → docs/Report.pdf | A Ch.1–2, B Ch.3 / M3 |
| Paper gốc + ≥3 nguồn khác | docs/latex/references.bib | A+B / M3 |
| Một public GitHub link, lịch sử commit, Colab public | README và checklist delivery | B; A review / M3 |
| File lớn: HF/Kaggle, ưu tiên snapshot công khai có sẵn | data/manifest.csv, public URL trong README | B/A / M1–3 |

## Phân bổ điểm cần lưu ý

Chương 1: 25–30% (tối ưu Julia 10%, Python 5%); Chương 2: 20%; Chương 3: **50%**,
chia đều hai ứng dụng. Theo bảng đề, Julia có tổng tối đa 100%, Python 95%.
Nhóm đã chọn Julia theo đề và kế hoạch; không được bỏ ứng dụng 2 để dồn vào benchmark.

## Điểm cần nhóm chốt

- Deadline Moodle chính thức, Group ID, tên/MSSV và GitHub usernames A/B.
- Bản dữ liệu cụ thể, public mirror HF/Kaggle và license; tính lại thống kê trên file thật.
- Schema đã khóa tại docs/SCHEMA.md: DNA −6..−1,+1..+6, chỉ số 25:36; không cần chọn lại.
- Grid minsup sau pilot, minconf Groceries và tiêu chí chọn pattern DNA.
- Các URL công khai và output test cuối chỉ điền sau khi có bằng chứng thật.
