# Ghi chú đọc paper — gói 01 / M1

**Mohammed J. Zaki. Scalable Algorithms for Association Mining.** IEEE Transactions
on Knowledge and Data Engineering, 12(3), 372–390, May/June 2000.
[DOI: 10.1109/69.846291](https://doi.org/10.1109/69.846291).
Đã đọc bản PDF người dùng cung cấp: `D:\eclat.zaki2000.pdf`, 19 trang.

## Phần cần đọc và ánh xạ mã

| Paper | Trang in / trang PDF | Nội dung cần nắm | Mã / bằng chứng |
|---|---|---|---|
| §2 | 373 / 2 | FIM, support count, association rules | utils.jl, rules.jl |
| §4.1 | 375 / 4 | Tid-list, support qua giao các TID, shrinking lists | structures.jl, baseline.jl |
| §4.2 | 376–377 / 5–6 | Prefix equivalence classes, phân rã sublattice | Pseudocode nhóm và baseline |
| §4.3.1, §5.2, Fig.12 | 377,381 / 6,10 | Bottom-up search trong lớp | Đối chiếu với DFS adaptation |
| §5.1 | 380–381 / 9–10 | Tính F1/F2; chi phí pairwise intersection và cách đếm cặp | Ghi rõ lựa chọn trong Ch.1 |
| §5.3–5.4 | 382 / 11 | Database scans và phân biệt sáu thuật toán | Giới hạn phạm vi chỉ Eclat |
| §7 | 383–388 / 12–17 | Thực nghiệm và hành vi theo đặc tính dữ liệu | Thiết kế phép đo, không chép số liệu |
| Appendix A | 388–390 / 17–19 | Search space và complexity dưới giả thiết | Phân biệt worst case với thực nghiệm |

## Ý tưởng cốt lõi

Với transaction database D có n giao dịch, `T(X)={tid | X ⊆ transaction_tid}`.
Support count `σ(X)=|T(X)|`; relative support `s(X)=σ(X)/n` khi n>0.
Do `T(X ∪ Y)=T(X) ∩ T(Y)`, đếm support chỉ cần giao tidsets, không quét lại
toàn bộ horizontal database cho từng candidate. Superset có support không lớn hơn
subset nên extension dưới threshold bị tỉa. Prefix partition giúp xử lý những
phần search space nhỏ hơn và kiểm soát intermediate tidsets.

## Lựa chọn trong kế hoạch: DFS Eclat basic

§5.4 gọi Eclat là prefix equivalence + **bottom-up** và xuất toàn bộ frequent itemset.
Kế hoạch nhóm chọn **DFS prefix extension**; tài liệu SPMF cũng mô tả phiên bản DFS.
Đây là lựa chọn triển khai cần giải thích rõ: giữ vertical representation, intersection,
prefix partition, tính đầy đủ và tính duy nhất; thay cách lập lịch duyệt trong lớp.
Không mô tả DFS của nhóm là bản sao nguyên Fig.12; không trộn MaxEclat, dEclat hay
maximal-only vào thuật toán cần xuất tất cả frequent itemset.

Các bước cần A/B chốt, rồi tự viết pseudocode chi tiết trong báo cáo:

1. Chuẩn hóa input, tạo F1 và tid-list; cố định thứ tự item.
2. Mỗi lời gọi giữ prefix P và danh sách extension có thứ tự.
3. Ghép extension tương thích, giao tidsets, giữ kết quả đủ support.
4. Emit mỗi `P∪{x}` một lần và đi sâu vào extension đứng sau x.
5. Quay lui, giải phóng các tidsets không dùng; output canonical độc lập thứ tự duyệt.

Phải chứng minh đường đi canonical duy nhất cho mỗi itemset và không mất extension
frequent. Phân biệt scan input/verticalization với intersection trong recursion.
Nếu F2 tính trực tiếp bằng intersections thay vì horizontal recovery/đếm cặp ở paper,
nêu lựa chọn và ảnh hưởng chi phí; không khẳng định tái tạo mọi tối ưu gốc.

## Complexity cần phân tích

Gọi m là số item, n số transaction và C là tập giao tidsets thực tế được thực hiện.
Giao hai sorted lists tốn O(|Ta|+|Tb|); bitset packed tốn khoảng O(ceil(n/w)) machine
words cho một AND/popcount, với w là số bit/word. Chi phí đọc dữ liệu ít nhất tỉ lệ
tổng số item xuất hiện. Có thể có đến `2^m−1` itemset khác rỗng; chi phí output phải
được tính đến. Không kết luận Eclat tuyến tính cho mọi dữ liệu chỉ vì một đồ thị
scalability gần tuyến tính. Memory cần tách input, active tidsets và output lưu giữ.

## Tối ưu dự kiến M2

So basic sorted list và BitVector cùng logic enumeration. BitVector giảm chi phí
membership/intersection ở dữ liệu phù hợp nhưng phải trả bitmap chiều dài n, nên
không mặc định tốt hơn trên sparse data. Đo cả runtime và peak RSS; buffer reuse,
ordering hoặc early stopping là hướng nghiên cứu tiếp, chỉ công bố cải thiện có đo.

Nguồn bổ sung để đối chiếu output/CLI:
[SPMF Eclat documentation](https://www.philippe-fournier-viger.com/spmf/Eclat_dEclat.php).
Paper là nguồn thuật toán chính; SPMF là tham chiếu thực thi, không sao chép mã nguồn.
