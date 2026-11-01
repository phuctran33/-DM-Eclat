# ECLAT: paper, DFS adaptation và cài đặt thực tế

Owner A — Nguyễn Đức Hưng. Đọc lại ngày 31/10/2026 từ bản PDF 19 trang
[SPMF lưu trữ](https://www.philippe-fournier-viger.com/spmf/zaki2000.pdf).
Nguồn chính: M. J. Zaki, *Scalable Algorithms for Association Mining*, IEEE TKDE
12(3), 372–390, 2000, [DOI](https://doi.org/10.1109/69.846291).
Không đọc/sao chép source thuật toán của SPMF; chỉ gọi JAR làm oracle.

## Đối chiếu chính xác với paper

| Phần | Trang in | Ý nghĩa đối với cài đặt |
|---|---|---|
| §2 | 373 | Itemsets, absolute/relative support, bước sinh luật riêng |
| §4.1 — Support Counting | 375 | Vertical tid-lists, giao và support; Lemma 4–6 |
| §4.2 — Lattice Decomposition | 376–377 | Phân hoạch theo prefix; lớp con độc lập |
| §5.1 | 380–381 | F1/F2; paper dùng horizontal recovery và bộ đếm cặp cho F2 |
| §5.2, Fig.12 | 381 | Bottom-up: dựng các lớp con rồi gọi đệ quy |
| §5.4 | 382 | Eclat = prefix equivalence + bottom-up; all frequent itemsets |
| §7 | 383–388 | Ảnh hưởng support, số giao dịch, width và bộ nhớ; không tái sử dụng số đo cũ |
| Appendix A | 388–390 | Kết quả complexity có giả thiết về graph sparsity/arboricity |

Paper định nghĩa Eclat theo bottom-up trong prefix classes. Cài đặt này giữ phép
giao tidsets, phân hoạch prefix và điều kiện support; đổi lịch sang **DFS prefix
extension**, xử lý xong một lớp con trước sibling tiếp theo. Không gọi pseudocode
bên dưới là bản chép Fig.12. Cũng không áp dụng khẳng định chỉ giữ hai lattice levels
của lịch bottom-up cho DFS: DFS còn giữ các ancestor classes đang hoạt động.

Một khác biệt nữa: F2 được tính bằng giao từng cặp F1 trong RAM. Không có bước
horizontal recovery, bảng đếm cặp tam giác, disk-based tid-list partitioning,
maximal-clique decomposition, diffsets hoặc maximal-only output của các biến thể khác.
[SPMF documentation](https://www.philippe-fournier-viger.com/spmf/Eclat_dEclat.php)
mô tả một phiên bản DFS; ở đây chỉ dùng tài liệu đó để đối chiếu API/output.

## Định nghĩa và invariant

D là **dãy** n giao dịch, mỗi giao dịch là một tập ID dương tăng dần. Hai dòng giống
nhau vẫn là hai quan sát. Với X khác rỗng, `T(X)={i∈1:n | X⊆D[i]}` và
`σ(X)=|T(X)|`. Relative support `s(X)=σ(X)/n` chỉ dùng khi n>0.
Với θ∈(0,1], ngưỡng `τ=max(1,ceil(θ*n))`; frequent khi `σ(X)≥τ`.
CSDL rỗng, hoặc τ>n, trả vector rỗng. Tập rỗng không nằm trong output.

`T(X∪Y)=T(X)∩T(Y)`. Nếu X⊆Y thì T(Y)⊆T(X), nên support không tăng khi mở rộng.
Do đó candidate dưới τ và mọi descendants của nó đều bị loại an toàn.
Trong `enumerate_class!`, mỗi atom có key `P⋅x`, tidset chính xác của key và support
đạt τ. Atoms cùng prefix P, extension x tăng theo ID; chỉ ghép với sibling đứng sau.

## Pseudocode tương ứng mã Julia

```text
MINE(D, τ, representation):
    validate D and τ; return [] if D empty or τ > |D|
    construct vertical singleton tidsets
    S ← frequent singleton atoms, sorted by ascending item ID
    F ← []
    DFS(S, τ, F)
    return F

DFS(S, τ, F):
    for i = 1 .. |S|:
        a ← S[i]                         # full key P⋅x; exact T(P⋅x)
        append Pattern(a.key, support(a.tids)) to F
        children ← []
        for j = i+1 .. |S|:
            b ← S[j]                     # key P⋅y, y > x
            U ← intersection(a.tids, b.tids)  # fresh owned storage
            if support(U) ≥ τ:
                append Atom(a.key ⋅ last(b.key), U) to children
        if children is not empty:
            DFS(children, τ, F)
```

`src/algorithm/baseline.jl` chứa `intersect_tids(::Vector{Int},::Vector{Int})`,
verticalization list và **một DFS chung**. Hai con trỏ của phép giao chỉ tiến;
khi bằng nhau ghi TID một lần rồi tăng cả hai. Hai danh sách cha không bị sửa.
`src/algorithm/bitset.jl` dispatch giao sang `a .& b`, support sang `count`.
Cả hai dùng `Vector{ListAtom}`/`Vector{BitsetAtom}` cụ thể trong hot loop.
Shared `Itemset`, `Pattern` và API v1.0.0 được giữ nguyên.

## Trace tự xây dựng

D = `[ [1,2,3], [1,3], [2,3], [1,2] ]`, τ=2:

| Item | TID-list | Support |
|---|---|---:|
| 1 | [1,2,4] | 3 |
| 2 | [1,3,4] | 3 |
| 3 | [1,2,3] | 3 |

Emit {1}:3. Lớp [1] có {1,2}:[1,4] và {1,3}:[1,2]. Emit {1,2}:2;
giao hai atom con chỉ còn [1], nên {1,2,3} bị prune. Emit {1,3}:2. Sau đó emit
{2}:3 và {2,3}:[1,3]:2; cuối cùng {3}:3. Tổng 6 itemsets. Writer sắp theo độ dài
rồi tuple, nên thứ tự dòng không phụ thuộc DFS. Ví dụ này có 4 giao dịch; fixture
`data/toy/basic.txt` thực tế có **5** giao dịch và **7** patterns tại 40%.

## Lập luận correctness

**Support:** singleton tids được thêm theo enumerate(D) nên tăng, đúng row ID,
không trùng; giao hai atom cùng prefix cho đúng tidset của union. Induction theo
độ dài key chứng minh mọi support phát ra chính xác.

**Duy nhất:** mỗi key tăng `x1<…<xk` có duy nhất đường prefix x1 → x1x2 → … → X.
Chỉ thêm extension lớn hơn item cuối, nên không có permutation khác hoặc nhánh
sibling nào sinh lại X. Pattern key canonical và không chứa empty itemset.

**Đầy đủ:** mọi prefix và sibling subset cần cho một frequent X đều frequent theo
anti-monotonicity. Chúng không bị prune; inductively phép giao sinh prefix tiếp theo
của X. Vì DFS duyệt hết các later siblings, cuối cùng X được emit đúng một lần.

**Validation/ownership:** parser reject item trùng, ID không dương và dòng không
sorted; không sửa ngầm. Blank/#/%/@ không tạo TID. API cho phép transaction rỗng
trong RAM (vẫn thuộc denominator); PreparedDataset và parser không tạo dòng rỗng.
Input caller không bị mutate. Mỗi giao list/bitmap cấp phát riêng, parent read-only.

## BitVector và chi phí

BitVector count singleton trước, chỉ cấp bitmap n bit cho F1, rồi đi qua transactions
lần nữa để đặt bit. `a .& b` tạo bitmap mới; `count` dùng packed support counting.
Không dùng Julia internal `chunks` API hoặc in-place AND có thể phá ancestor mask.
Count được gọi cả khi lọc và khi emit; hiện chưa fuse AND/popcount hoặc reuse buffer.

Gọi L là tổng item occurrences, m số item, C tập candidate joins, F tập output và
w số bit/word. Basic verticalization O(L+m log m); giao hai lists O(|Ta|+|Tb|).
Tổng giao là tổng chi phí này trên C. BitVector cần O(L+|F1|⌈n/w⌉) để tạo masks
(ngoài sorting); mỗi candidate cần O(⌈n/w⌉) word operations cho AND/count.
Pattern constructor còn sort/validate keys: tổng O(ΣX∈F |X| log |X|), và writer
sort output rồi ghi ít nhất Σ|X| item IDs. Worst case |F|=2^m−1; DFS không làm mất
output explosion. Appendix A không cung cấp một bound tuyến tính vô điều kiện cho
cài đặt lưu toàn bộ F này.

Bộ nhớ tách horizontal input O(L), vertical singleton structures, active ancestor
classes, một giao tạm và output O(Σ|X|). Lists lưu Int TIDs (8 byte/TID trên máy đo);
bitmaps có payload khoảng 8⌈n/64⌉ byte/mask cộng object/array overhead. Bitmap không
co ngắn khi support giảm: sparse intersections có thể bất lợi. DFS nhả tham chiếu
lớp con khi quay lui, nhưng GC quyết định lúc thu hồi; RSS còn bao gồm runtime/JIT.
Không đồng nhất payload với peak process RSS.

## Bằng chứng kiểm tra và giới hạn tích hợp

`tests/test_correctness.jl` dùng exhaustive subset counting độc lập cho 5 fixtures,
20 DB ngẫu nhiên (seed 42), edge cases và word-boundary sizes. `tests/test_spmf.jl`
so toàn bộ map với 5 references thật tại 40%, không chỉ so count; manifest pin input,
output và JAR SHA-256. `scripts/prepare_spmf.py --references` tái tạo bằng Java.
`tests/test_rules.jl` kiểm mọi hướng luật, consequent nhiều item, thiếu subset và
PreparedDataset → mine. Preprocessing Groceries/DNA của B vẫn pending, không được
coi bài test PreparedDataset là xác minh hai pipeline trên dữ liệu thực.

Full suite mặc định bật cả backends và references. Lệnh và stdout cuối nằm trong
`docs/verification.md`, `results/logs/`; số liệu đo và phạm vi timer được mô tả tại
`docs/experiments.md` và Chương 2. B cần review adaptation và tích hợp ứng dụng.
