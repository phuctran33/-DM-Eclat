# Công cụ tham chiếu

Tải SPMF từ trang chính thức, đặt `spmf.jar` ở đây, không commit JAR.
Ghi phiên bản/commit SPMF, Java version và SHA-256 JAR trong log thực nghiệm.
Chỉ gọi binary làm oracle/benchmark, không sao chép Java source vào miner Julia.


Nhánh B tái tạo references bằng scripts/prepare_references_b.py, pin SPMF 2.64b.
Máy kiểm thử có Java 8 mặc định; truyền --java đường dẫn Java 21 trong CLion hoặc
một JDK >=21 phù hợp. Không cần đổi PATH/Java hệ thống. Log/hash thật tại
 docs/member-b-validation/spmf/. JAR vẫn được ignore.
