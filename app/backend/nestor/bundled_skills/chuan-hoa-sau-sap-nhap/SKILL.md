---
name: chuan-hoa-sau-sap-nhap
description: "Rà và cập nhật tên đơn vị, địa danh, cấp hành chính cũ trong văn bản theo bảng đối chiếu, mô hình hai cấp từ 01/7/2025. Dùng cho thư mục văn bản hàng loạt."
---

# Chuẩn hóa văn bản sau sáp nhập đơn vị hành chính

## Khi nào dùng / không dùng
- DÙNG: một văn bản hoặc cả thư mục còn tên phường/xã/quận/huyện cũ, tên cơ quan cũ; cần lập bảng phát hiện, bảng đối chiếu cũ - mới, cập nhật mẫu văn bản (mẫu tờ trình, công văn) sang tên đơn vị mới; kiểm tra số liệu báo cáo có đơn vị ghi tên cũ.
- KHÔNG dùng: khi chưa có nguồn đối chiếu và người dùng muốn bạn tự 'biết' đơn vị cũ nhập vào đâu (không được tự suy ra, xem Quy tắc).
- Bối cảnh: từ 01/7/2025 chính quyền địa phương tổ chức hai cấp (tỉnh/thành phố và xã/phường/đặc khu), không còn cấp huyện/quận; nhiều đơn vị cấp xã được sắp xếp, đổi tên. Tên chính thức của từng đơn vị mới phải lấy từ nghị quyết/quyết định hoặc bảng của địa phương do người dùng cung cấp, cần kiểm chứng.

## Hỏi lại (gom một lần bằng ask_user questions)
1. Phạm vi: file/thư mục nào; có giữ nguyên bản gốc không (mặc định luôn giữ).
2. Bảng đối chiếu chính thức: file .xlsx/.csv hai cột 'Tên cũ' | 'Tên mới' (và cột Ghi chú/Căn cứ nếu có). Chưa có thì hỏi người dùng có file danh mục không; nếu không, chỉ phát hiện và liệt kê, KHÔNG sửa.
3. Có sửa cả địa chỉ, tên cơ quan ký, thẩm quyền ('UBND huyện …' → cấp nào) hay chỉ tên địa danh.
4. Cách xử lý văn bản lịch sử (đã ban hành trước 01/7/2025): thường KHÔNG sửa, chỉ ghi chú.

## Công cụ
| Việc | Công cụ |
|---|---|
| Quét tên cũ trong file/thư mục theo bảng đối chiếu | place_name_check(path, mapping_path) |
| Đọc nội dung để rà ngữ cảnh | read_document |
| Mẫu bảng đối chiếu | templates/bang-doi-chieu.csv (đọc bằng skills_read) |
| Tạo bảng phát hiện/đối chiếu .xlsx | create_xlsx |
| Văn bản chỉnh sửa đúng thể thức | vanban_types, vanban_write_docx, review_vn_document (kiểm cảnh báo cấp hành chính cũ) |
| So bản gốc - bản đã chỉnh | compare_documents(path_a, path_b) |
| Xử lý hàng loạt thư mục lớn | run_script (thử trên 1-2 file trước) |

## Quy trình
1. Liệt kê file (list_dir/glob). Với mỗi file chạy place_name_check(path, mapping_path) để lấy các chỗ khớp tên cũ.
2. Lập sheet 'Phát hiện': File | Vị trí (đoạn/bảng) | Cụm tìm thấy | Tên mới đề xuất | Căn cứ (dòng trong bảng đối chiếu) | Trạng thái (tự động/cần xác nhận).
3. Phân loại từng chỗ: (a) khớp duy nhất trong bảng → đề xuất đổi; (b) tên cũ ứng với NHIỀU tên mới (một đơn vị tách) hoặc nhiều tên cũ → một tên mới → 'cần xác nhận'; (c) không có trong bảng → 'không có căn cứ'.
4. Nếu người dùng đồng ý sửa: tạo bản mới tên khác (ví dụ ten-file-da-chuan-hoa.docx), giữ nguyên bản gốc. Văn bản dựng lại thì dùng vanban_write_docx để thể thức đúng.
5. Kiểm tra lại bản mới: place_name_check phải không còn tên cũ ngoài danh sách 'cần xác nhận' hoặc văn bản lịch sử; compare_documents để chắc chỉ phần tên đổi.
6. Báo: số file quét, số chỗ đã đổi, số chờ xác nhận, số không có căn cứ.

## Mẫu đầu ra
- Sheet 'Phát hiện' như bước 2. Sheet 'Cần xác nhận': Cụm | Các khả năng | Câu hỏi cho người có thẩm quyền.
- Ví dụ: 'UBND phường A, quận B' trong bảng ánh xạ → 'UBND phường C' (căn cứ dòng 12 của bảng); 'huyện Hòa Vang' không có trong bảng → 'không có căn cứ', hỏi người dùng nguồn.
- templates/bang-doi-chieu.csv: Tên cũ,Tên mới,Căn cứ (số, ngày văn bản), Ghi chú.

## Quy tắc quyết định
- CHỈ dùng bảng đối chiếu của người dùng hoặc đã được họ xác nhận trong cuộc trò chuyện. Không tự suy đơn vị cũ nhập vào đâu, kể cả khi bạn 'nhớ'.
- Tên cũ trùng nhau giữa các nơi (nhiều 'phường 1'): chỉ đổi khi có thêm thành phần phân biệt (quận/thành phố) trong chính câu đó.
- Văn bản đã ban hành trước 01/7/2025: để nguyên, đánh dấu 'văn bản lịch sử', trừ khi người dùng bảo sửa.
- Cấp huyện/quận trong thẩm quyền ký, quyết định: KHÔNG tự đổi thẩm quyền, chuyển sang 'cần xác nhận'.

## Checklist tự kiểm
- [ ] Bản gốc còn nguyên; bản đã chỉnh có tên khác.
- [ ] Mỗi thay đổi có căn cứ từ bảng đối chiếu của người dùng.
- [ ] Trường hợp mơ hồ được liệt kê là 'cần xác nhận', không tự quyết.
- [ ] place_name_check trên bản mới không còn tên cũ ngoài danh sách đã nêu.
- [ ] compare_documents cho thấy chỉ các cụm tên đổi (không đổi nội dung khác).

## Lỗi thường gặp
- Đổi hàng loạt bằng tìm-thay thế làm hỏng ngữ cảnh (ví dụ 'Quận 1' trong tên đường).
- Đổi cả văn bản lịch sử, gây sai sự thật.
- Quên chữ ký, nơi nhận, địa chỉ ở đầu/cuối trang và trong bảng.

## Giới hạn
- Không tự quyết tên mới của đơn vị khi không có nguồn. Điều không chắc: ghi 'cần kiểm chứng'.
- Không ghi đè bản gốc; không gửi văn bản đã sửa.
