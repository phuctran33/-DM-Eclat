# M2 người B — kết quả và bàn giao

Ngày thực hiện: **10/11/2026**, Asia/Saigon. Nhánh `feat/member-b-m2-applications`,
base main `1f7a980` đã chứa PR A/B trước. Không sửa core Eclat/rules của A.

## Đã triển khai

`groceries_application` và `dna_application` gọi **cả list lẫn BitVector** của nhóm
và so toàn bộ itemset/support map trước khi sinh kết quả. CLI
`scripts/run_applications.jl` đọc config đã chốt, ghi vào staging rồi chuyển sang
output mới/rỗng; từ chối ghi đè kết quả cũ. Metadata `run.toml` ghi config, runtime,
SHA-256 đầu vào, mã Julia và từng artifact, counts và trạng thái đối chiếu hai backend.

Groceries giữ minsup=0.005, minconf=0.60: count tối thiểu ceil(0.005×9835)=50.
Pilot có đủ 22 luật để trình bày top-10 nên giữ ngưỡng ban đầu, không lựa ngưỡng
để tăng lift sau khi xem kết quả. Mine đầy đủ **1.001 patterns**, sinh mọi split
khác rỗng đủ confidence rồi xếp theo lift/confidence/support giảm, union length/IDs tăng.

DNA dùng minsup=0.20 riêng từng lớp: EI 153/765, IE 154/766, N 331/1654.
Mine đầy đủ: **381 EI, 209 IE, 48 N patterns**. EI có patterns dài đến 6 items;
không cắt output mining ở độ dài 4. Sau đó hợp candidates dài 2–4, đếm lại trên
cả ba lớp: **463 rows**. Có **864** cặp candidate/lớp dưới ngưỡng nhưng count >0;
không dùng absence trong frequent output làm support 0.

## Groceries: top-10 thật

| Rank | Tiền kiện → hậu kiện | Count | Support (%) | Confidence (%) | Lift |
|---:|---|---:|---:|---:|---:|
| 1 | citrus fruit | root vegetables | whole milk → other vegetables | 57 | 0.5796 | 63.33 | 3.2732 |
| 2 | pip fruit | root vegetables | whole milk → other vegetables | 54 | 0.5491 | 61.36 | 3.1714 |
| 3 | pip fruit | whipped/sour cream → other vegetables | 55 | 0.5592 | 60.44 | 3.1236 |
| 4 | onions | root vegetables → other vegetables | 56 | 0.5694 | 60.22 | 3.1120 |
| 5 | root vegetables | tropical fruit | yogurt → whole milk | 56 | 0.5694 | 70.00 | 2.7396 |
| 6 | other vegetables | pip fruit | root vegetables → whole milk | 54 | 0.5491 | 67.50 | 2.6417 |
| 7 | butter | whipped/sour cream → whole milk | 66 | 0.6711 | 66.00 | 2.5830 |
| 8 | pip fruit | whipped/sour cream → whole milk | 59 | 0.5999 | 64.84 | 2.5374 |
| 9 | butter | yogurt → whole milk | 92 | 0.9354 | 63.89 | 2.5004 |
| 10 | butter | root vegetables → whole milk | 81 | 0.8236 | 63.78 | 2.4961 |

1. **Luật #1:** citrus fruit + root vegetables + whole milk → other vegetables.
   Có 57/90 giỏ thỏa hậu kiện (63,33%), so với tỷ lệ nền 1.903/9.835 = 19,35%;
   lift 3,273. Có thể thử gợi ý/bố trí rau khi giỏ đã có nhóm trái cây, rau củ và sữa.
   Toàn luật chỉ gặp ở 57 giỏ nên không xem đây là hành vi phổ quát.
2. **Luật #5:** root vegetables + tropical fruit + yogurt → whole milk.
   56/80 = 70%, so với tỷ lệ nền sữa 2.513/9.835 = 25,55%; lift 2,740.
   Gợi ý mua kèm sữa cho nhóm giỏ này là giả thuyết cần A/B test trước áp dụng.
3. **Luật #9:** butter + yogurt → whole milk. 92/144 = 63,89%, lift 2,500;
   support 0,9354% lớn hơn luật #1 nhưng lift thấp hơn nên đứng sau theo tiêu chí đã chốt.
   Tiền kiện ngắn và số quan sát lớn hơn có thể thuận tiện hơn cho thử nghiệm bán chéo.

Lift đo mức lệch so với độc lập trong dữ liệu quan sát, không phải mức tăng doanh thu
hoặc tác động nhân quả của khuyến mãi. Các luật chia sẻ nhiều item, không phải
các bằng chứng độc lập. Ngưỡng support thấp, số đếm nhỏ và lựa chọn top theo cùng
dữ liệu có thể làm thứ hạng không ổn định; cần dữ liệu thời gian khác/A-B test.

## DNA: patterns thực sự được khai thác

Window 25:36 tương ứng -6..-1,+1..+6; mapping 48 IDs cố định. Bỏ 5 mẫu ambiguous
trong window, giữ EI 765, IE 766, N 1.654. Nhãn không đưa vào transaction mining.
Đây là bảng chọn theo xếp hạng chung, có đại diện độ dài 2, 3 và 4; toàn bộ 463
rows nằm ở `results/applications/dna_patterns.csv`.

| Rank | Pattern | EI count/support (%) | IE count/support (%) | N count/support (%) | Span |
|---:|---|---:|---:|---:|---:|
| 1 | pos=+1;base=G | pos=+2;base=T | 758 / 99.08 | 108 / 14.10 | 98 / 5.93 | 0.9316 |
| 2 | pos=-2;base=A | pos=-1;base=G | 388 / 50.72 | 762 / 99.48 | 127 / 7.68 | 0.9180 |
| 3 | pos=+1;base=G | pos=+2;base=T | pos=+5;base=G | 651 / 85.10 | 22 / 2.87 | 15 / 0.91 | 0.8419 |
| 13 | pos=-1;base=G | pos=+1;base=G | pos=+2;base=T | pos=+5;base=G | 514 / 67.19 | 22 / 2.87 | 2 / 0.12 | 0.6707 |

- (+1,G),(+2,T) gặp ở 99,08% EI nhưng 14,10% IE và 5,93% N: co-occurrence
  bên phải ranh giới có khác biệt lớn giữa các nhãn. Không gán IE/N bằng 0 vì
  không đạt minsup=20% ở hai lớp đó.
- (-2,A),(-1,G) gặp ở 99,48% IE, 50,72% EI, 7,68% N. Đây là một pattern
  mô tả ở bên trái ranh giới; không phải một quy tắc phân loại hoàn hảo.
- Pattern 4 item rank 13 gặp ở EI 514/765, IE 22/766, N 2/1654. Điều kiện dài
  hơn cụ thể hơn nhưng support EI giảm; một hậu tố dài hơn không tự có giá trị
  dự báo cao hơn.

EI/IE là exon–intron/intron–exon theo [UCI](https://doi.org/10.24432/C5M888).
Các nhận xét trên là mô tả counts của nhóm, không suy ra cơ chế sinh học,
accuracy classifier hay p-value. Lớp N lớn hơn, nên dùng denominator riêng từng lớp.
Cửa sổ/ngưỡng đã chọn, bỏ mẫu ambiguity và chọn pattern trên cùng dữ liệu giới hạn
khả năng khái quát; muốn dự báo phải có đánh giá trên tập độc lập.

## Kiểm chứng

- Full Julia suite: **787 pass**, gồm 25 checks mới cho mining application/end-to-end
  artifacts, lớp N dưới ngưỡng nhưng count khác 0, guard output và config sai.
- Python audit kiểm mọi count emitted, mọi split luật đủ ngưỡng, labels/ranking,
  top-10 prefix và toàn bộ union candidates DNA bằng phép đếm độc lập. Không dùng FIM library.
- Java SPMF 2.64b pin JAR: cả Groceries/EI/IE/N khớp **100% toàn map**, counts
  lần lượt 1.001/381/209/48. Truyền threshold nằm trong đúng absolute-count bin
  tránh floating boundary của SPMF; không giới hạn độ dài output.
- Hai lần pipeline phải có cùng artifact hashes; runtime metadata có thể khác
  giữa Julia/OS. Notebook chạy actual cells, không giả lập flag thành công.

## Chạy lại

```text
python scripts/prepare_application_data.py --dataset all
julia --project=. scripts/run_applications.jl --output results/applications-rerun
python -B scripts/verify_application_results.py --output results/applications-rerun --java PATH_TO_JAVA_21
julia --project=. tests/runtests.jl
python -B scripts/run_notebook.py
```

Notebook local dùng `ECLAT_JULIA`/`ECLAT_JAVA` nếu executable không ở PATH hoặc Java
mặc định quá cũ. Colab notebook tự tải Julia có kiểm checksum và cài Java 21.

[**Mở notebook M2 trên Colab**](https://colab.research.google.com/github/phuctran33/-DM-Eclat/blob/feat/member-b-m2-applications/notebooks/demo.ipynb).
GitHub Actions `applications-notebook` chạy từ checkout Ubuntu sạch, tải nguồn thật,
chạy mọi cell và upload artifacts. Local/CI Linux không được ghi là remote Colab.
Phiên này chưa điều khiển được runtime Google Colab; cần mở link, Run all và lưu
output để reviewer xác nhận tiêu chí Colab tối thiểu. Đây là phần nghiệm thu
ngoài môi trường thực thi hiện tại, không được đánh dấu pass chỉ vì CI xanh.

## Files chính

- `src/applications/pipelines.jl`: API orchestration, không thay core của A.
- `scripts/run_applications.jl`: CLI/config và export atomic.
- `scripts/verify_application_results.py`: count/rule audit và Java oracle.
- `results/applications/`: CSV đầy đủ/top10, DNA table, frequent outputs, mapping,
  audit, run metadata và log/provenance SPMF. Raw/transaction data không commit.
- `notebooks/demo.ipynb`: notebook đầy đủ M2, các cờ ứng dụng/SPMF mặc định bật.
- `docs/latex/sections/03-applications.tex`: phân tích thực, không còn TODO kết quả ứng dụng.

Gói 05/06 có implementation/evidence sẵn cho A review; checkbox nghiệm thu trong
issue briefs vẫn do reviewer xác nhận. Report.pdf 10–15 trang và final Colab cold-run
M3 không được suy ra đã xong từ việc hoàn tất code/kết quả M2.
