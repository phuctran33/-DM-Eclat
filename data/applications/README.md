# Nguồn dữ liệu ứng dụng

- Groceries dùng CSV snapshot Git pin revision và SHA-256. Mỗi dòng là
  một giỏ, được chuyển thành các cặp `basket_id,item_name`. CSV snapshot
  không có điều khoản tái phân phối riêng trong manifest, nên tải từ nguồn
  như hướng dẫn. [arules Groceries](https://mhahsler.github.io/arules/reference/Groceries.html)
- Splice dùng `splice.data` có nhãn, mã quan sát và chuỗi 60 vị trí. Cả bản
  Szeged và file trong ZIP UCI đều phải khớp cùng SHA-256. Giấy phép UCI
  CC BY 4.0 yêu cầu ghi nguồn. [UCI](https://doi.org/10.24432/C5M888)

Từ repo root, chạy `python3 scripts/prepare_application_data.py --dataset all`
để tải cả hai, hoặc chọn `groceries` hay `splice`. Mỗi lượt lưu nguồn thực tế
và kết quả chuẩn hóa. Dữ liệu đầu vào được sinh tại chỗ từ
[manifest](../manifest.csv). Quy tắc chuyển giao dịch nằm ở
[schema](../../docs/SCHEMA.md) và hai notebook ứng dụng.
