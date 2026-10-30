# Hai ứng dụng theo kế hoạch — gói 05 và 06

Owner B, reviewer A. A hỗ trợ association rules và tích hợp miner.
Mọi kết quả cuối lấy từ cài đặt Julia của nhóm; SPMF chỉ dùng để kiểm chứng.
Hai pipeline phải chạy được trong Colab từ raw data/mirror đã ghi provenance.

## Groceries: basket analysis

Schema v1.0.0 đã chốt tại [SCHEMA.md](SCHEMA.md); nguồn snapshot thực tế cần được
xác minh. Helper nhận canonical CSV `basket_id,item_name` tại
`data/applications/groceries.csv`, trả `PreparedDataset`. Một basket là một
transaction, product name là một item; bỏ item trùng trong basket, giữ basket trùng
giữa các lượt mua. Tạo vocabulary theo thứ tự ổn định, lưu mapping ID↔tên sản phẩm.
Xuất thống kê số basket, item và width sau chuyển đổi.

M2: helper `groceries_transactions` → `mine(...; backend=:list/:bitset)` →
`association_rules`. Với A,B khác rỗng, rời nhau, X=A∪B:

`support=σ(X)/n`, `confidence=σ(X)/σ(A)`, `lift=confidence/(σ(B)/n)`.

Pilot bắt đầu ở minsup `0.005`, minconf `0.60`; điều chỉnh sau pilot phải ghi lý do
và run config. Nếu không đủ 10 luật, kiểm tra threshold và báo minh bạch;
không bịa thêm. Lưu `groceries_rules.csv` với items/tên, absolute counts, support,
confidence, lift, rank; sắp lift giảm dần và tie-break xác định. B giải thích ít nhất
3 luật trong top-10: kết hợp sản phẩm, gợi ý kinh doanh, baseline phổ biến, giới hạn.
Lift cao từ support thấp có thể không ổn định; co-occurrence không chứng minh nhân quả.

## DNA: UCI Splice, 12 vị trí, EI/IE/N

Nguồn gốc: [UCI Molecular Biology (Splice-junction Gene Sequences)](https://archive.ics.uci.edu/dataset/69/molecular+biology+splice+junction+gene+sequences),
[dataset DOI](https://doi.org/10.24432/C5M888). UCI mô tả 3,190 mẫu, 60 vị trí và
các lớp EI (exon→intron), IE (intron→exon), N (neither). Kiểm lại counts trên file tải.
Ký tự ngoài A/C/G/T như D/N/S/R biểu thị ambiguity; N trong sequence khác nhãn lớp N.

Schema đã khóa **12 vị trí**: relative −6..−1,+1..+6, Julia index **25:36** trong
sequence 60 base. Mapping đủ 48 IDs với base order A,C,G,T;
`id=4*(slot-1)+base_index`. Không đổi cửa sổ âm thầm theo pattern nhìn đẹp.

Mỗi sequence là transaction; item phải là **(position, base)**, ví dụ `(-2,G)`.
Chỉ mã hóa A/C/G/T thành IDs 1..48 theo mapping cố định khi không có ambiguity.
Không mã hóa thành tập {A,C,G,T} vì sẽ mất vị trí và dễ thành pattern tầm thường.
Giữ class label, sample ID ngoài transaction. Chính sách ambiguity đã chốt: bỏ cả
sample nếu window chứa ký tự ngoài A/C/G/T; ngoài window vẫn được giữ. Structural
errors phải fail. Thống kê trước/sau theo lớp, không expand thành giao dịch giả.

Pilot minsup `0.20` cho từng lớp; mẫu số relative support là số sample hợp lệ **của lớp đó**.
Để trình bày lấy pattern 2–4 item từ output đầy đủ, không bật giới hạn độ dài trong
correctness/benchmark. Hợp các candidate từ ba lớp; đếm lại trực tiếp trên mọi lớp
để điền support cho pattern không frequent ở lớp khác. Không xem missing output
là support 0. Lưu `dna_patterns.csv` có decoded pattern, length, count và support
EI/IE/N, chênh lệch support và criterion xếp hạng.

Diễn giải khác biệt co-occurrence ở cửa sổ splice, class imbalance, ambiguity,
selection effects và ngưỡng. Đây là khai thác pattern mô tả; không tự khẳng định
phát hiện cơ chế sinh học hoặc chất lượng bộ phân loại khi chưa có đánh giá tương ứng.

## Gate M2 và nội dung Chương 3

Notebook cần raw→transactions→miner→bảng→diễn giải, có seed/mapping/config và xuất
artifact. Kết quả basic/bitset khớp; B kiểm SPMF cùng input/threshold. Mỗi ứng dụng có
data provenance, quyết định transactionization, phương pháp, kết quả thật, ý nghĩa
và giới hạn. M3 viết hoàn chỉnh Chương 3 và chạy lại từ Colab sạch.
