# Chuẩn bị vấn đáp ECLAT

Chạy toy trước, tự tính tidsets rồi lần một kết quả từ mã đến bảng báo cáo.
[Cấu trúc và luồng thực thi](ARCHITECTURE.md).

1. **ECLAT đang trả gì?** `mine` trả mọi itemset khác rỗng có absolute support
   đạt `min_count`. `Pattern.items` là tuple ID tăng dần và `support` là số
   giao dịch chứa itemset. Relative support là số đó chia số giao dịch.

2. **Vì sao dùng vertical layout?** Với mỗi item, lưu các vị trí giao dịch chứa
   nó. Một vị trí chứa hợp hai itemset khi nó nằm trong cả hai tidsets. Số TID
   trong giao chính là support. `baseline.jl` tránh quét lại horizontal input
   cho từng candidate.

3. **DFS sinh đủ và không lặp bằng cách nào?** Mỗi class có cùng prefix và
   extensions tăng dần. Chỉ ghép với sibling đứng sau, nối extension cuối và
   giao tidsets. Mỗi key có một đường tăng dần. Các tiền tố của một tập frequent
   đều frequent, nên đường đó tồn tại.

4. **Pruning xảy ra khi nào?** Support của superset không lớn hơn subset. Giao
   dưới `min_count` bị loại cùng hậu duệ. Toy `basic` có 5 hàng, minsup 40% cho
   count 2, nên `(1,2,3)` với support 2 vẫn ra output. Có 7 patterns.

5. **Khác paper Zaki ở đâu?** Giữ vertical tidsets và prefix equivalence
   classes. Code duyệt sâu ngay sau khi dựng một lớp con và tạo F2 bằng giao
   singleton. Fig. 12 của paper dựng các lớp con rồi gọi đệ quy. Bản nhóm không
   dùng horizontal recovery để đếm cặp.

6. **Multiple dispatch và ownership ở đâu?** Public API đổi Symbol thành tag.
   Julia chọn methods theo positional argument type. DFS dùng một atom type
   cụ thể, hai methods `intersect_tids` trả bộ nhớ mới. AND tại chỗ có thể
   sửa tidset cha và làm sai các sibling sau.

7. **So sánh chi phí list và bitmap.** Giao list hai con trỏ tốn tối đa
   `O(|Ta|+|Tb|)`; giao và đếm bitmap tốn `O(ceil(n/64))` từ máy trên máy đo.
   Mask chứa n bits dù giao thưa. DFS giữ các lớp đang duyệt và toàn bộ output,
   có thể tới `2^m−1` itemsets với m items.

8. **Vì sao Retail có thể chậm hơn?** Ít item đạt ngưỡng và nhiều giao nhỏ nên
   lợi ích AND bị hạn chế. Bản BitVector vẫn đọc để đếm singleton rồi dựng
   mask. Ở ngưỡng trung bình, tỉ số median warm Basic/BitVector trên Retail
   là 0,91, còn Chess là 5,10. Đây là số của cấu hình đã đo.

9. **Tại sao 0,07 trên 100 giao dịch cho count 7?** CLI dùng rational từ chuỗi,
   không đưa số qua Float64 trước ceil. Khi benchmark, SPMF nhận giá trị nằm
   giữa khoảng cho cùng absolute count. Item trùng trong một hàng bị từ chối,
   còn hai hàng trùng nội dung vẫn được đếm riêng.

10. **Oracle có vai trò gì?** Vét cạn đếm trực tiếp trên toy, kiểm lỗi có thể
    xảy ra ở DFS chung. SPMF là cài đặt Java riêng. So itemset → support,
    missing/extra/wrong support, chẳng hạn sparse ở 40% có output rỗng hợp lệ.

11. **Hai vùng thời gian khác gì?** End-to-end tính startup/JIT, I/O, mining
    và chờ process cho cả ba backend. Warm Julia đo đọc/kiểm và khai thác sau
    warm-up trong cùng process, loại ghi file và bước kiểm equality. Chỉ
    so sánh backend ở vùng đo tương ứng.

12. **Peak RAM lấy từ đâu?** `/usr/bin/time` lấy peak RSS của process, gồm
    runtime, input, intermediate và output. `@timed` đếm bytes cấp phát
    tích lũy trong vùng Julia. Chúng trả lời hai câu hỏi khác nhau.

13. **Tin bộ số liệu benchmark dựa vào gì?** Có cùng input/hash/count, exact
    map trước đo, kiểm output từng lần, năm repeats và median/min–max.
    Có 35 cấu hình, 875 số đo OK và 70 phép đối chiếu. Kết quả đo giới hạn
    trong một máy, thứ tự chạy và file cache đã dùng.

14. **Scalability và width thay đổi gì?** Retail dùng nested subsets từ một
    permutation seed 42 và giữ relative minsup. Thử width giữ n, m và
    minsup, chọn uniform items không hoàn lại. Kích thước output cũng đổi,
    nên không suy ra độ phức tạp tuyến tính từ đường thời gian.

15. **Vì sao chọn Groceries?** Một lượt mua định nghĩa tự nhiên một transaction.
    Mapping của 169 sản phẩm giúp giải mã luật từ 9.835 giỏ. Ngưỡng 0,5%
    tương ứng 50 giỏ và minconf 0,60 cho 1.001 itemsets, 22 luật và đủ top-10.

16. **Support, confidence, lift khác nhau thế nào?** Với hai vế A, B và n
    giỏ, support là count(A∪B)/n, confidence là count(A∪B)/count(A), lift là
    confidence chia count(B)/n. Luật hạng 1 có 57/90 giỏ, confidence 63,33%,
    lift 3,273 so với nền other vegetables 19,35%. Là giả thuyết gợi ý mua
    kèm cần kiểm trên nhóm đối chứng. Hai ví dụ khác ở Chương 3.

17. **Vì sao chọn cửa sổ Splice 25:36?** Lấy sáu vị trí mỗi phía ranh giới đã
    căn chỉnh, vị trí là một phần của item. Có 48 IDs cho 12×4. Loại 5 mẫu
    có ký tự mơ hồ trong cửa sổ, giữ 3.185/3.190 mẫu. Không đưa nhãn vào miner.

18. **Vì sao tính support theo lớp rồi đếm lại?** EI/IE/N có 765/766/1.654
    mẫu giữ. Cùng ngưỡng 20% tương ứng 153/154/331 counts. Mine được
    381/209/48 patterns và hợp 463 candidates độ dài 2–4. Một mẫu dưới
    ngưỡng ở lớp khác vẫn có thể có count dương, nên phải recount.

19. **Ý nghĩa sinh học và giới hạn?** Cặp GT ngay sau ranh giới có support
    99,08% ở EI và 5,93% ở N. Cặp AG ngay trước ranh giới có support 99,48%
    ở IE và 7,68% ở N. Phù hợp motif donor/acceptor thường gặp, nhưng đây
    là mô tả trên tập mẫu đã căn chỉnh, chưa đánh giá classifier hay cơ chế.
    [Nguồn đối chiếu motif GT/AG](https://doi.org/10.1093/nar/28.21.4364).

20. **Tối ưu tiếp và demo nhanh?** Thử chọn list/mask theo mật độ tidset để cải
    thiện nhánh thưa. Thử gộp AND và popcount hoặc dùng lại buffer ở nơi không
    còn tham chiếu để giảm cấp phát. Muốn demo từ repo root, chạy các lệnh dưới,
    rồi mở CSV ứng dụng và hình chương 2 theo [README](../README.md).

```bash
julia --project=. scripts/mine.jl --input data/toy/basic.txt --output .tools/demo-basic.txt --minsup 40% --backend list
julia --project=. scripts/compare_spmf.jl .tools/demo-basic.txt tests/reference/spmf/basic.txt
python -B scripts/run_notebook.py
```
