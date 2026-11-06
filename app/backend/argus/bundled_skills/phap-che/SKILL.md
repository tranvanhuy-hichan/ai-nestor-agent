---
name: phap-che
description: "Rà hợp đồng, quy chế, dự thảo văn bản: liệt kê điều khoản rủi ro, so sánh bản sửa, đề xuất chỉnh. Dùng khi cần ý kiến pháp chế hỗ trợ có dẫn nguồn."
---

# Pháp chế hỗ trợ (rà hợp đồng, quy chế, dự thảo)

## Khi nào dùng / không dùng
- DÙNG: rà hợp đồng (lao động, mua bán, dịch vụ, thuê); rà dự thảo quy chế, quy định nội bộ, quyết định; đối chiếu dự thảo với quy định trong kho tài liệu; so sánh hai bản dự thảo; soạn công văn trả lời kiến nghị dựa trên quy định đã có.
- KHÔNG dùng: tư vấn thay luật sư, kết luận ai đúng ai sai trong tranh chấp, dự đoán kết quả tòa án, giải thích pháp luật cho người dân (xem giai-thich-phap-ly).
- Đây là ý kiến hỗ trợ, KHÔNG phải kết luận pháp lý ràng buộc; quyết định thuộc người có thẩm quyền hoặc luật sư.

## Hỏi lại (gom một lần bằng ask_user questions)
1. Tài liệu cần rà (file) và vị thế của người dùng (bên A hay B trong hợp đồng; cơ quan ban hành quy chế).
2. Mục tiêu: rà rủi ro, rà đủ điều khoản, so với quy định cụ thể nào, hay soạn văn bản trả lời.
3. Kho văn bản pháp luật hiện có (kb_search) và quy định nội bộ liên quan.
4. Mức độ: liệt kê vấn đề hay kèm bản sửa đề xuất.

## Công cụ
| Việc | Công cụ |
|---|---|
| Đọc hợp đồng, quy chế (Word/PDF/ảnh scan) | read_document, view_image |
| Tìm quy định áp dụng trong kho | kb_search |
| So sánh bản gốc - bản sửa, hai bản dự thảo | compare_documents(path_a, path_b) |
| Tra cứu bổ sung từ nguồn chính thống trên mạng | web_search, web_fetch (nêu rõ nguồn, ngày truy cập) |
| Bảng rủi ro, bảng đối chiếu | create_xlsx / create_docx |
| Công văn trả lời, văn bản hành chính | vanban_types, vanban_write_docx, review_vn_document |
| Xuất PDF | convert_to_pdf(path) |

## Quy trình
1. Đọc toàn văn; xác định loại tài liệu, các bên, giá trị, thời hạn, luật điều chỉnh.
2. Lập danh sách điều khoản theo nhóm: đối tượng và phạm vi; giá và thanh toán; giao nhận/nghiệm thu; bảo hành; thời hạn, gia hạn; chấm dứt; phạt vi phạm và bồi thường; bất khả kháng; bảo mật; giải quyết tranh chấp; sở hữu trí tuệ; điều khoản chung.
3. Với từng điều khoản: Có/không; rõ/mơ hồ; lệch bất lợi cho người dùng không; mâu thuẫn với điều khoản khác không; thiếu gì so với thông lệ.
4. Căn cứ: kb_search lấy quy định. Chỉ nêu điều khoản pháp luật ĐÃ ĐỌC từ nguồn; không có thì ghi 'cần kiểm chứng' kèm tên văn bản dự kiến (nếu chắc), không tự điền số điều.
5. Bảng rủi ro: STT | Vị trí (điều, khoản, trang) | Vấn đề | Mức độ (cao/trung bình/thấp) | Căn cứ | Đề xuất sửa (câu chữ cụ thể).
6. Nếu được yêu cầu bản sửa: tạo file mới tên khác, dùng compare_documents để liệt kê thay đổi; không ghi đè gốc.
7. Kết luận ngắn: vấn đề nghiêm trọng nhất (tối đa 5), và câu hỏi cần người có thẩm quyền/luật sư quyết.

## Mẫu đầu ra
| Vị trí | Vấn đề | Mức | Căn cứ | Đề xuất |
|---|---|---|---|---|
| Điều 7.2 | Phạt vi phạm 20% giá trị hợp đồng không phân biệt mức vi phạm | Cao | cần kiểm chứng mức trần theo luật hiện hành | Điều chỉnh theo từng mức vi phạm, nêu mức tối đa |
Ví dụ rà quy chế: 'Điều 5 không nêu cấp có thẩm quyền xử lý khiếu nại' → mức Trung bình, đề xuất bổ sung 'Chủ tịch/Thủ trưởng đơn vị'.

## Quy tắc quyết định
- Không chắc điều luật còn hiệu lực/được sửa đổi: ghi 'cần kiểm chứng', không khẳng định.
- Điều khoản có lợi cho người dùng vẫn nêu nếu có rủi ro bị vô hiệu/không khả thi.
- Mâu thuẫn giữa hợp đồng và phụ lục: nêu cả hai và hỏi.
- Vấn đề thuộc phán đoán (đúng/sai trong tranh chấp, thuế, hình sự): chuyển luật sư.

## Checklist tự kiểm
- [ ] Mỗi vấn đề có vị trí điều khoản, mức độ và đề xuất sửa cụ thể.
- [ ] Căn cứ pháp lý chỉ là điều đã đọc từ nguồn, còn lại là 'cần kiểm chứng'.
- [ ] Đã nêu rõ đây là ý kiến hỗ trợ, không phải kết luận pháp lý ràng buộc.
- [ ] File gốc không bị ghi đè; bản sửa (nếu có) tên khác và đã so bằng compare_documents.
- [ ] Đã nêu tối đa 5 vấn đề nghiêm trọng nhất và câu hỏi cho người có thẩm quyền.

## Lỗi thường gặp
- Bịa số điều khoản/số văn bản pháp luật.
- Kết luận 'hợp pháp/vi phạm' chắc chắn.
- Bỏ sót phụ lục, điều khoản tham chiếu chéo.
- Đề xuất câu chữ làm đổi ý của các bên.

## Giới hạn
- Không đưa tư vấn pháp lý ràng buộc, không đại diện ký kết, không gửi văn bản đi.
- Không bịa văn bản pháp luật. Tài liệu hợp đồng nhạy cảm chỉ xử lý trong thư mục làm việc.
