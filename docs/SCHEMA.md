# Schema v1.0.0 — hợp đồng chính thức giữa A và B

Chốt ngày **30/10/2026** theo yêu cầu nhóm. Áp dụng cho Eclat basic, BitVector,
Groceries, UCI Splice DNA, test và artifacts thực nghiệm. Kiểu Julia nằm ở
`src/schemas.jl`; cấu hình dạng máy đọc ở `schemas/contracts.toml`.

**Schema đã chốt không có nghĩa thuật toán/preprocessing đã cài đặt xong.**
Các hàm TODO tiếp tục fail rõ ràng. Muốn thay schema phải sửa version, tài liệu,
config, caller và test trong cùng thay đổi, có A/B review.

## 1. Quy ước chung

- Văn bản UTF-8; CSV theo RFC 4180, có đúng header, dấu phẩy, quote trường chứa
  dấu phẩy/quote/newline; quote bên trong viết thành `""`. Writer dùng LF.
- Item ID là Int dương, mapping liên tiếp `1..m`. Transaction là Vector{Int}
  tăng dần, không trùng item; tên và nhãn không đi vào miner.
- TID là chỉ số **1-based trong danh sách đã chuẩn hóa**. `row_id` là ID quan sát
  ổn định; source-line và sample ID được lưu riêng, không đánh đồng với TID.
- Giữ các quan sát có cùng nội dung nếu là hai quan sát khác nhau.
- Preprocessing không sinh transaction rỗng. Lỗi cấu trúc báo lỗi; mẫu DNA bị loại
  phải có audit. Miner nhận CSDL rỗng và trả output rỗng.
- Counts là số nguyên; support/confidence là tỉ lệ `[0,1]`, không phải %. Không
  làm tròn trước khi lọc/xếp hạng. Giá trị % chỉ dùng trong hiển thị.
- Trường bắt buộc không rỗng. CSV provenance: ô chưa biết rỗng + status=pending;
  metric không đo/không áp dụng là `NA`, không phải 0.
- Không cắt output hoặc đổi dữ liệu/ngưỡng âm thầm để correctness pass.

## 2. Interface A/B: PreparedDataset

```julia
struct PreparedDataset
    dataset_id::String
    transactions::Vector{Vector{Int}}
    item_labels::Dict{Int,String}
    row_ids::Vector{String}
    classes::Union{Nothing,Vector{String}}
end
```

| Trường | Ý nghĩa / invariant |
|---|---|
| dataset_id | `groceries` hoặc `splice` cho hai ứng dụng |
| transactions | Input trực tiếp của mine, không chứa metadata/nhãn lớp |
| item_labels | ID→tên đọc được; tên unique; có thể chứa ID chưa xuất hiện |
| row_ids | Cùng độ dài/thứ tự transactions; không rỗng, không trùng |
| classes | nothing cho Groceries; vector EI/IE/N theo thứ tự mẫu DNA |

B triển khai `groceries_transactions(path)::PreparedDataset` và
`splice_transactions(path; positions=25:36)::PreparedDataset`.
A chỉ nhận `prepared.transactions`; B giữ metadata để decode, phân lớp và báo cáo.
Stats/audit xuất file riêng. Constructor kiểm alignment/mapping/transactions;
chuẩn hóa domain cụ thể thuộc helper của B.

## 3. Groceries

### Đầu vào chuẩn của helper

B viết notebook adapter chuyển snapshot nguồn về canonical long CSV
`data/applications/groceries.csv`, giữ nguyên nội dung và ranh giới giỏ hàng:

```csv
basket_id,item_name
basket-001,whole milk
basket-001,bread
basket-002,bread
```

Mỗi dòng là basket/item; header cố định. Basket ID là string, giữ số 0 đầu.
Nguồn không có ID: adapter gán theo số dòng basket gốc và lưu lineage.
Nguồn customer/date: ghi rõ khóa nhóm; không tự coi mỗi dòng sản phẩm là một basket.

### Chuẩn hóa cố định

1. Basket ID trim đầu/cuối, phân biệt hoa/thường, bắt buộc không rỗng.
2. Product name: Unicode NFC → lowercase → strip → collapse whitespace nội bộ
   thành một space. Không stemming, dịch tên, fuzzy merge hay gộp đồng nghĩa.
3. Tên rỗng hoặc CSV sai cấu trúc: fail, nêu dòng lỗi; không âm thầm bỏ.
4. Cùng basket/item lặp lại: giữ một item; ghi số dòng trùng bị gộp trong audit.
5. Sort product names lexicographic không phụ thuộc locale, gán IDs 1..m.
6. Sort basket IDs lexicographic để xác định transaction order. Giữ hai basket có
   ID khác nhau dù nội dung giống nhau. Chuỗi `10` có thể đứng trước `2`.
7. classes=nothing; mapping dùng tên chuẩn hóa; tên gốc vẫn ở raw nguồn.

Pilot ban đầu: minsup **0.005**, minconf **0.60**. Được điều chỉnh sau pilot nếu
ghi lại giá trị/lý do trong run metadata; đó là tham số thực nghiệm, không đổi schema.

## 4. UCI Splice DNA

Nguồn: [UCI Splice](https://archive.ics.uci.edu/dataset/69/molecular+biology+splice+junction+gene+sequences),
[DOI](https://doi.org/10.24432/C5M888). Raw `splice.data`, ba CSV fields không header:
`class,source_id,sequence`. UCI mô tả 60 vị trí và alphabet có ambiguity symbols.

### Window và mapping đã khóa

Lấy **Julia indices 25:36**, relative positions
`[-6,-5,-4,-3,-2,-1,+1,+2,+3,+4,+5,+6]`, không có vị trí 0.
Mỗi mẫu hợp lệ tạo đúng 12 item, mỗi item là `(position,base)`.

Với slot=1..12, base order A,C,G,T tương ứng base_index=1..4:

```text
item_id = 4 × (slot − 1) + base_index
label   = pos=<relative_position>;base=<base>
```

ID 1 = `pos=-6;base=A`, ID 4 = `pos=-6;base=T`,
ID 25 = `pos=+1;base=A`, ID 48 = `pos=+6;base=T`.
Mapping **luôn đủ 48 item**, độc lập subset/class đang xét.

### Validity, ambiguity, metadata

- Trim/uppercase class; chỉ EI/IE/N. Source ID trim, bắt buộc không rỗng.
- Sequence bỏ whitespace, uppercase, yêu cầu đúng 60 ký tự. Chỉ nhận alphabet
  IUPAC DNA `ACGTRYSWKMBDHVN`; ký tự khác/độ dài sai/class sai: fail và nêu dòng.
- Nếu **window 12 vị trí** có ký tự ngoài A/C/G/T: bỏ cả mẫu với reason
  `ambiguous_window`. Ambiguity ngoài window không làm mẫu bị loại.
- Không expand ambiguity thành nhiều giao dịch, không gộp sequence giống nhau.
- Giữ thứ tự dòng raw của mẫu được giữ; row_id=`splice:<raw_line_number>`.
  Source ID gốc lưu riêng; nhãn EI/IE/N không đi vào transaction.
- Sau lọc không còn mẫu hoặc một lớp rỗng: pipeline ứng dụng báo lỗi, không chia 0.

Pilot minsup **0.20** cho từng lớp; absolute threshold = ceil(0.20*n_class), với
n_class là số mẫu hợp lệ **của chính lớp đó**.

## 5. Eclat core và SPMF

```julia
mine(transactions::Vector{Vector{Int}}, min_count::Integer;
     backend::Symbol=:list)::Vector{Pattern}
```

Backend là :list hoặc :bitset; min_count>=1. Pattern có tuple items canonical và
support::Int. Emit mọi frequent itemset khác rỗng đúng một lần; support bằng ngưỡng
được giữ. Thứ tự trong RAM không là correctness requirement; writer sort
`(length(items),items)`. Hai backend có cùng tập kết quả.

`parse_minsup("0.4") == parse_minsup("40%")`; threshold dùng exact rational.
SPMF input mỗi dòng một transaction numeric; blank/metadata/comment #/%/@ bị bỏ.
Output ví dụ `1 2 #SUP: 3`, không kèm nhãn lớp, timestamp, utility hay TID suffix.

M1 reference cố định **40%** cho basic/dense/sparse/duplicates/boundary.
Ghi input hash, JAR hash, version/lệnh/output hash vào manifest. Không giới hạn độ
dài output khi kiểm correctness. So canonical map, báo missing/extra/wrong_support.
Match rate = exact matching keys / union keys; hai tập rỗng cho rate 1, count 0.

## 6. Association rules

```julia
association_rules(patterns::Vector{Pattern}, n::Integer;
                  minconf=3//5)::Vector{AssociationRule}
```

Input frequent output **đầy đủ**. Với A,B khác rỗng, rời nhau, X=A∪B:

| Field | Type / công thức |
|---|---|
| antecedent / consequent | Itemset tuple canonical |
| support_count | Int, σ(X) |
| antecedent_count / consequent_count | Int, σ(A) / σ(B) |
| n_transactions | Int, số basket hợp lệ |
| support | Float64, σ(X)/n |
| confidence | Float64, σ(X)/σ(A) |
| lift | Float64, confidence/(σ(B)/n) |

Constructor tính ratios từ counts. Hàm sinh mọi luật đủ minconf từ frequent itemset
độ dài ≥2; không giới hạn một item bên phải. Lọc minconf bằng exact count ratio.
Thiếu subset support là lỗi thay vì 0. Sort:
`(-lift,-confidence,-support,total_item_count,antecedent,consequent)`.
Trả mọi luật; CSV top-10 lấy 10 dòng đầu cùng schema, nếu ít hơn báo số thực.

## 7. DNA comparison

```julia
compare_dna_patterns(
    dataset::PreparedDataset,
    patterns_by_class::AbstractDict{String,Vector{Pattern}}
)::Vector{DNAPatternComparison}
```

Dict đủ keys EI/IE/N. Mine đầy đủ từng lớp, hợp candidates frequent ở ít nhất một
lớp, lọc **2–4 item**, đếm lại trên cả ba lớp. Không có trong frequent output không
có nghĩa support 0. Mỗi row có items, counts/denominators/supports EI/IE/N và
`support_span=max(supports)-min(supports)`.
Count 0 hợp lệ; mọi denominator >0. Sort giảm support_span, giảm max class support,
tăng length rồi tuple items. Đây là xếp hạng mô tả, không là p-value.

## 8. Artifacts và files

Header chính xác nằm trong `schemas/contracts.toml`. `schemas/tables/` chứa file
header rỗng, **không phải kết quả thực nghiệm**.

| File khi chạy thật | Nội dung |
|---|---|
| data/applications/processed/<dataset>/transactions.txt | Numeric SPMF input |
| .../items.csv | item_id,item_label,position,base; position/base rỗng cho Groceries |
| .../observations.csv | tid,row_id,source_id,class; class rỗng cho Groceries |
| .../preparation_audit.csv | dataset/class/reason/count; ALL cho Groceries |
| results/applications/groceries_rules.csv | Mọi luật đã sort, kèm decoded labels |
| results/applications/groceries_top10.csv | Tối đa 10 dòng đầu, cùng schema |
| results/applications/dna_patterns.csv | Pattern/count/denominator/support ba lớp |
| tests/reference/spmf/manifest.csv | Provenance reference thực sự từ SPMF |
| results/raw/benchmark_runs.csv | Một row mỗi lần đo, có metric_scope |
| results/correctness/comparisons.csv | Kết quả đối chiếu đầy đủ |

ID list trong CSV là các số cách một space, không dùng JSON/Julia repr. Labels
nối ` | ` để hiển thị, không dùng để reconstruct vì label có thể chứa ký tự đó;
IDs và mapping là nguồn decode. Floats export đủ 17 significant digits.
Rank bắt đầu từ 1 sau sort; length là pattern length/union length của luật.

Audit: mỗi lớp có row reason=kept và các row drop reason nếu có, count là số
observations. Riêng reason=duplicate_item_rows_collapsed của Groceries đếm duplicate
long rows, không đếm observations bị loại. Structural errors fail cả preparation.

Benchmark: run_id unique, seed=42; status trong ok/timeout/oom/error; metric_scope
trong internal_read_mine/end_to_end. Không gộp hai phạm vi đo lên cùng đường cong.
Thiếu RSS là NA, không lấy allocated_bytes thay peak RSS. Worker hiện còn cần
runner/monitor/aggregation; schema xác định output đích, chưa tự cài đặt chúng.

## 9. Phân công và trạng thái

| Owner | Phải triển khai theo schema |
|---|---|
| A / M1 | Eclat basic + CLI → Vector{Pattern} |
| B / M1 | Toy/SPMF references/tests, source adapters/provenance chuẩn bị M2 |
| A / M2 | BitVector; hỗ trợ association_rules |
| B / M2 | Groceries/DNA preprocessing/comparison/artifact writers/Colab |
| A / M3 | Benchmark runner/RSS/aggregation/plotting |
| B / M3 | Benchmark correctness, Chương 3, Colab và bàn giao |

Shared types/validation đã có. Miner, preprocessing, rule generation và DNA
comparison vẫn TODO. URL snapshot/revision/hash chưa tải xác minh thì pending;
đó là provenance thực tế, không phải schema chưa quyết định.
