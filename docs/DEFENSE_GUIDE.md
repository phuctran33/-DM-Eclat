# Chuẩn bị vấn đáp ECLAT

Buổi vấn đáp dự kiến từ 07–12/12/2026, theo trao đổi ngày 25/11. Tập trung
trình bày phần mỗi người đã làm, công cụ đã dùng, lý do chọn phương pháp và
bài học rút ra. Giảng viên hướng tới trao đổi về bài làm thay vì yêu cầu
tính tay công thức hoặc chạy code tại chỗ. Mỗi người nên đọc cả ba chương
và tập giải thích hai quyết định do thành viên còn lại phụ trách.
[Phân công](../README.md) · [Kiến trúc](ARCHITECTURE.md)

1. **Nhóm giải quyết bài toán gì?** Tìm mọi tập item khác rỗng xuất hiện
   trong đủ số giao dịch, kèm số giao dịch chứa tập đó. Cùng miner Julia
   được dùng cho benchmark, luật giỏ hàng và mẫu quanh điểm nối DNA.

2. **ECLAT khai thác bằng cách nào?** Mỗi item có tập TID ghi các giao dịch
   chứa nó. Giao hai tập TID cho đúng các giao dịch chứa hợp hai itemset.
   DFS mở rộng theo thứ tự item ID và tỉa cả nhánh khi support dưới ngưỡng.
   Nhờ đó mỗi itemset được xét theo một đường tăng dần mà không cần quét
   lại toàn bộ dữ liệu ngang tại mỗi ứng viên.

3. **Nhóm bám theo bài Zaki ở đâu?** Giữ biểu diễn dọc và các lớp tương đương
   tiền tố. Cài đặt nhóm dựng cặp đầu bằng giao singleton rồi đi sâu ngay
   khi có một lớp con. Hai kiểu tidset dùng chung DFS, Julia dispatch theo
   kiểu dữ liệu tại bước giao. Mỗi phép giao trả tidset riêng để bảo toàn
   tidset của các nhánh anh em. [Bài gốc](https://doi.org/10.1109/69.846291)

4. **Vì sao chọn BitVector? Khi nào chọn Basic?** BitVector đóng gói mỗi
   giao dịch bằng một bit và giao theo từ máy, có lợi khi nhiều tidset dày.
   Basic giao hai danh sách TID đã sắp bằng hai con trỏ và phù hợp với giao
   thưa. Ở ngưỡng trung bình, tỉ số thời gian warm Basic/BitVector là 5,10
   trên Chess và 0,91 trên Retail. Chi phí dựng mask và bộ nhớ bitmap trở
   nên đáng kể khi mỗi item xuất hiện trong ít giao dịch.

5. **Vì sao chọn bốn benchmark?** Chess và Mushroom làm rõ tác động của
   dữ liệu dày với chiều rộng lần lượt 37 và 23. Retail có nhiều item hiếm
   và đủ lớn để chia tập con. T10I4D100K bổ sung trường hợp thưa tổng hợp
   100.000 hàng. Demo thử các kho công khai và kiểm hash sau chuẩn hóa để
   mọi backend đọc đúng input đã đo. [Nguồn và đặc điểm](../data/README.md#benchmark)

6. **SPMF và unit test phát hiện lỗi gì?** Vét cạn và các ca ngẫu nhiên kiểm
   logic DFS chung. Java SPMF là oracle độc lập chạy cùng dữ liệu và cùng
   ngưỡng đếm. Nhóm kiểm toàn bộ map itemset → support, gồm tập thừa, tập
   thiếu và support sai, nên hai đầu ra bằng số lượng vẫn có thể trượt.
   Có cả ca đúng bằng ngưỡng và ca output rỗng hợp lệ.

7. **Nhóm kiểm soát ngưỡng giữa Julia và Java thế nào?** CLI đọc ngưỡng từ
   chuỗi hữu tỉ. Harness chọn tỉ lệ nằm trong cùng khoảng ngưỡng đếm cho
   SPMF, tránh khác biệt tại biên làm tròn. Khi giải thích kết quả, chỉ
   rõ hai backend dùng cùng số giao dịch tối thiểu.

8. **Đo runtime và RAM ra sao?** End-to-end tính từ tiến trình mới, gồm
   startup, JIT, đọc, khai thác và ghi, dùng để so ba backend. Warm Julia
   đo đọc và khai thác sau warm-up, trước khi ghi file và so map. Peak
   RSS từ `/usr/bin/time` là đỉnh bộ nhớ cư trú toàn tiến trình. Bytes do
   `@timed` báo là lượng cấp phát tích lũy trong vùng đo Julia.

9. **Kết quả nói lên điều gì?** 35 cấu hình có 70 phép so full map và 875
   phép đo OK. Median và min–max của năm lượt cho thấy BitVector có lợi ở
   Chess, nhưng đổi biểu diễn có thể tốn thời gian hơn trên Retail hoặc
   tốn RSS hơn trên T10. Muốn biết vì sao, cần xem mật độ tidset, chi phí
   dựng biểu diễn, ngưỡng và số tập phải xuất. [Kết quả](../results/README.md)

10. **Scalability và thí nghiệm độ rộng giúp hiểu gì?** Retail lấy các tập
    con lồng nhau từ cùng hoán vị seed 42 và giữ relative minsup. Thử độ
    rộng giữ số hàng, số item và ngưỡng, lấy các tiền tố từ hoán vị từng
    hàng. Số tập phổ biến cũng thay đổi theo dữ liệu. Một đường xu hướng
    trên máy đo chưa đủ để kết luận độ phức tạp tổng quát.

11. **Nhóm tiền xử lý Groceries thế nào?** Mỗi dòng nguồn xác định một giỏ.
    Pipeline chuẩn hóa tên, gộp item trùng trong cùng giỏ rồi mã hóa 169
    sản phẩm; mọi giỏ vẫn có ID riêng. Sau khai thác 9.835 giỏ, Julia giải
    mã lại tên hàng trong 22 luật. Top-10 xếp theo lift sau khi lọc confidence.

12. **Support, confidence và lift có nghĩa gì khi đọc một luật?** Support
    mô tả độ phổ biến của hai vế cùng xuất hiện. Confidence cho biết trong
    các giỏ có vế trái, bao nhiêu phần cũng có vế phải. Lift so tỉ lệ này
    với mức nền của vế phải. Luật hạng 1 có confidence 63,33% và lift 3,273,
    gợi ý thử trưng bày hoặc giới thiệu mua kèm. Quan hệ quan sát cần kiểm
    bằng thí nghiệm trước khi kết luận về tác động kinh doanh.

13. **Vì sao DNA phải mã hóa vị trí?** Cùng một base ở hai vị trí mang ý
    nghĩa khác nhau quanh ranh giới đã căn chỉnh. Nhóm chọn sáu vị trí
    mỗi bên, tạo tối đa 48 ID vị trí–base. Từ 3.190 mẫu, giữ 3.185 mẫu có
    cửa sổ A/C/G/T. Nhãn EI/IE/N dùng chia lớp, còn giao dịch chỉ chứa ID
    vị trí–base.

14. **Vì sao có bước đếm lại theo lớp?** Mine riêng cho EI/IE/N ở ngưỡng
    20% được 381/209/48 tập. Sau khi hợp 463 mẫu dài 2–4, đếm trực tiếp
    trên từng lớp để có cả support dương dưới ngưỡng ở lớp khác. Nhờ đó
    so được tần suất giữa các lớp có kích thước khác nhau.

15. **Mẫu DNA và hai giới hạn ứng dụng là gì?** Cặp GT ngay sau ranh giới
    có support 99,08% ở EI và 5,93% ở N. Cặp AG ngay trước ranh giới có
    support 99,48% ở IE và 7,68% ở N. Kết quả phù hợp motif donor và
    acceptor thường gặp trong mẫu căn chỉnh. Việc tổng quát sang dữ liệu
    mới cần validation riêng. Luật giỏ hàng cũng phụ thuộc cửa hàng,
    khoảng thời gian lấy mẫu và cách đặt ngưỡng.
    [Nguồn motif GT/AG](https://doi.org/10.1093/nar/28.21.4364)

16. **Nhóm học được gì và sẽ thử tiếp điều gì?** So toàn bộ map phát hiện
    lỗi mà đếm output bỏ sót. Chọn cấu trúc dữ liệu theo mật độ có triển
    vọng hơn dùng một backend cho mọi case. Hai hướng tiếp theo là thử
    tidset thích nghi và giảm cấp phát bằng cách gộp phép AND với đếm bit.
    Khi bàn giao cần giữ hash input, log đúng vùng đo và nguồn tải đủ ổn
    định để người khác kiểm lại kết quả. [Phương pháp](experiments.md)
