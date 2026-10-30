# Bốn benchmark theo kế hoạch

Chuẩn bị `chess.txt`, `mushroom.txt`, `retail.txt`, `T10I4D100K.txt` ở đây.
Không có dữ liệu benchmark được tải sẵn trong template.

Ưu tiên public snapshot có sẵn trên Hugging Face/Kaggle theo đề. Điền URL public,
revision/version, license, SHA-256 và đường dẫn local vào `data/manifest.csv`.
Nguồn tham chiếu: [SPMF datasets](https://www.philippe-fournier-viger.com/spmf/index.php?link=datasets.php)
và [FIMI](http://fimi.uantwerpen.be/data/).

Chỉ dùng transaction format, không nhầm với sequence format có `-1/-2`.
Tính thống kê từ file thật. File lớn không commit; notebook phải tải và chuẩn bị được.
