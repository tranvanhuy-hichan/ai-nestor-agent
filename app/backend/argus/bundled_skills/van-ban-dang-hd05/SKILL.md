---
name: van-ban-dang-hd05
description: "Soạn dự thảo nghị quyết, chỉ thị, kết luận, thông báo, báo cáo của cấp ủy theo HD 05-HD/VPTW. Dùng cho văn bản Đảng, KHÔNG dùng cho văn bản nhà nước."
---

# Văn bản của Đảng theo Hướng dẫn 05-HD/VPTW

## Khi nào dùng / không dùng
- DÙNG: dự thảo nghị quyết, chỉ thị, kết luận, quy định, quy chế, thông báo (kết luận cuộc họp), báo cáo, tờ trình, công văn, biên bản của tổ chức Đảng (đảng ủy, chi bộ, ban thường vụ, ủy ban kiểm tra, các ban đảng).
- KHÔNG dùng: văn bản của UBND, HĐND, cơ quan nhà nước (dùng van-thu-nd30: quốc hiệu - tiêu ngữ, thể thức khác hẳn).
- Hai hệ thống KHÁC NHAU: văn bản Đảng không có quốc hiệu - tiêu ngữ nhà nước mà có tiêu đề Đảng Cộng sản Việt Nam, tên cơ quan ban hành, số và ký hiệu theo hệ thống của Đảng, địa danh - ngày tháng, tên loại + trích yếu, thể thức ký (T/M, K/T, chức danh của Đảng), nơi nhận. Chi tiết (cỡ chữ, lề, vị trí từng thành phần, ký hiệu loại văn bản, cách ghi số) phải đối chiếu bản Hướng dẫn gốc; skill này là khung thực hành, KHÔNG thay thế văn bản gốc.

## Hỏi lại (gom một lần bằng ask_user với questions)
1. Cấp ủy/cơ quan ban hành (đảng ủy phường ……, chi bộ ……, ban ……) và cấp trên trực tiếp (nếu thể thức cần ghi).
2. Loại văn bản và nội dung chính: kết luận cuộc họp nào (ngày, chủ trì, thành phần), nghị quyết về vấn đề gì.
3. Số và ký hiệu (nếu đã cấp), ngày ban hành, người ký và chức danh (đồng chí …, bí thư/phó bí thư), có ký thay (T/M, K/T) không.
4. Có mẫu/văn bản cũ cùng cơ quan để theo cấu trúc không (read_document).
5. Mức độ mật/khẩn (chỉ khi người dùng nói rõ).

## Công cụ
| Việc | Công cụ |
|---|---|
| Đọc mẫu, văn bản cũ, ảnh nghị quyết | read_document, view_image |
| Dựng file Word dự thảo | create_docx (Markdown), trình bày tối thiểu rồi báo rõ cần đối chiếu HD 05 |
| Kiểm tra nội dung (ngôn ngữ, ngày, số) | review_vn_document chỉ đối chiếu thể thức NĐ 30, dùng để rà chính tả/số chứ KHÔNG coi kết quả là đúng thể thức Đảng |
| Tìm văn bản gốc/hướng dẫn trong kho của người dùng | kb_search |
| So sánh bản thảo với bản cũ | compare_documents(path_a, path_b) |
| Xuất PDF | convert_to_pdf(path) |

## Quy trình
1. Xác định loại văn bản và đọc kho tài liệu (kb_search) xem người dùng đã có bản Hướng dẫn/mẫu của đơn vị chưa. Có thì ưu tiên mẫu đó.
2. Khung nội dung theo loại (xem Mẫu bên dưới). Giữ giọng văn trang trọng, câu ngắn, đúng thuật ngữ của Đảng; không dùng văn phong hành chính nhà nước.
3. Viết nội dung chỉ dựa trên dữ liệu người dùng cung cấp (kết luận cuộc họp, ý kiến, số liệu). Không thêm chủ trương, chỉ tiêu, nhân sự mà họ không đưa.
4. Tạo file bằng create_docx: dòng đầu là tên cơ quan ban hành; tiếp theo số, ký hiệu và địa danh - ngày; tên loại + trích yếu; nội dung; nơi nhận; chức danh ký. Mọi chỗ chưa có thông tin ghi '……'.
5. Ở phần đầu file ghi rõ dòng "DỰ THẢO: cần đối chiếu thể thức với Hướng dẫn 05-HD/VPTW trước khi ban hành" (xóa trước khi chính thức).
6. Báo người dùng danh sách điểm cần đối chiếu: font và cỡ chữ, ký hiệu loại văn bản, cách ghi số, chức danh ký, mức độ mật/khẩn, chữ viết tắt cơ quan.

## Mẫu khung nội dung (không phải thể thức chính thức)
- Thông báo kết luận cuộc họp: (1) Thời gian, địa điểm, chủ trì, thành phần; (2) Các ý kiến thảo luận chính; (3) Kết luận (đánh số, mỗi nhiệm vụ có đơn vị chủ trì và thời hạn nếu cuộc họp nêu); (4) Tổ chức thực hiện.
- Nghị quyết chuyên đề: Căn cứ - Đánh giá thực trạng - Quan điểm, mục tiêu - Nhiệm vụ, giải pháp - Tổ chức thực hiện.
- Báo cáo sơ kết/tổng kết công tác xây dựng Đảng: Kết quả (theo từng nhóm công tác) - Hạn chế, nguyên nhân - Phương hướng nhiệm vụ. Số liệu đảng viên, chi bộ, kết nạp: lấy từ người dùng.

## Quy tắc quyết định
- Người dùng nhờ 'soạn theo thể thức Đảng' nhưng không có tài liệu hướng dẫn: vẫn soạn dự thảo theo khung trên, nói thẳng rằng thể thức chính thức phải đối chiếu.
- Người dùng gửi file đã có quốc hiệu - tiêu ngữ nhà nước: hỏi lại, có thể họ nhầm hệ thống văn bản.
- Nội dung nhạy cảm (nhân sự, kỷ luật, kiểm tra): chỉ soạn dự thảo từ dữ liệu họ cung cấp, nhắc giữ bí mật, không gợi ý kết luận thay tổ chức.

## Checklist tự kiểm
- [ ] File .docx đã tạo bằng create_docx và có dòng cảnh báo 'DỰ THẢO cần đối chiếu HD 05'.
- [ ] Không có quốc hiệu, tiêu ngữ nhà nước ở đầu văn bản.
- [ ] Mọi nhân sự, số liệu, ngày, chỉ tiêu có trong dữ liệu người dùng đưa; chỗ thiếu là '……'.
- [ ] Đã nêu danh sách điểm cần đối chiếu thể thức cho người dùng.
- [ ] Mỗi nhiệm vụ trong kết luận có đơn vị phụ trách và thời hạn (hoặc '……' nếu nguồn không nói).

## Lỗi thường gặp
- Dùng thể thức nhà nước (quốc hiệu, tiêu ngữ) cho văn bản Đảng.
- Tự thêm nhiệm vụ, chỉ tiêu, nhân sự không có trong cuộc họp.
- Quên nơi nhận và chức danh ký, hoặc dùng 'TM.' của nhà nước thay cho cách ghi của Đảng.

## Giới hạn
- Chỉ là bản dự thảo để cán bộ văn phòng cấp ủy hoàn thiện; không ban hành, không ký.
- Không bịa số hiệu, ký hiệu, chức danh, nội dung kết luận. Điều không chắc về thể thức: ghi 'cần đối chiếu HD 05-HD/VPTW'.
- Không đưa tài liệu nội bộ của Đảng lên dịch vụ bên ngoài.
