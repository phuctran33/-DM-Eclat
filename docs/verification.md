# Kết quả kiểm tra template

Ngày kiểm tra: **30/10/2026**. Môi trường: Windows, Julia **1.11.4**, repo-local
depot. Phiên bản 1.9 được cấu hình trong CI nhưng chưa chạy local.

## Đã kiểm tra

```text
SPMF I/O and canonical comparison:       14 / 14 pass
Threshold boundaries and API validation: 19 / 19 pass
Eclat correctness:                       pending / skipped
SPMF comparison:                         pending / skipped
```

Julia hiển thị `@test_skip` ở cột `Broken`; hai dòng pending ở trên không phải
bằng chứng thuật toán đã đúng. Chưa cài đặt miner hoặc có reference SPMF thật.

Các kiểm tra bổ sung đã đạt:

- CLI `--help` chạy; mining dừng bằng thông báo TODO và không tạo output giả.
- Comparator exit 0 khi bằng nhau, exit 1 khi sai/missing/extra, exit 2 khi file sai.
- Synthetic generator tạo đúng số dòng/width và tái lập byte-for-byte với seed 42.
- Subsets 10/25/50/75/100% đúng kích thước và nested theo một hoán vị cố định.
- Benchmark worker dừng rõ ở miner TODO; chưa công bố runtime hoặc peak RAM.
- Năm expected toy được kiểm lại bằng exhaustive subset counting ở 40%, độc lập SPMF.
- Project/configs parse TOML; notebook parse mọi Python code cell, không có output giả.
- Chín local issue briefs đúng ba module; các link Markdown local cụ thể tồn tại.

Đã sửa parser để luôn đóng file khi dữ liệu sai, tránh giữ file handle trên Windows.

## Chưa xác minh và phần nhóm cần làm

Eclat basic/BitVector, SPMF equality, ứng dụng Groceries/DNA, benchmark đầy đủ,
peak RSS, remote Colab cold-run và build LaTeX/PDF **chưa thực hiện**. Nguồn Report.tex
có sẵn; chưa có `docs/Report.pdf`. Test mặc định pass không thay gate M1/M2/M3.

Lệnh chạy lại hạ tầng:

```text
julia --project=. tests/runtests.jl
julia --project=. scripts/mine.jl --help
```

Full tests sau triển khai: bật `ECLAT_TEST_MINER=1`, `ECLAT_TEST_SPMF=1`,
`ECLAT_TEST_BACKENDS=list,bitset`. Ở M1 chỉ kiểm `list` theo kế hoạch.
