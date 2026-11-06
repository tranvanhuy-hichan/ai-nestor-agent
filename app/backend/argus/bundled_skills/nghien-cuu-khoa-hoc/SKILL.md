---
name: nghien-cuu-khoa-hoc
description: Hướng dẫn làm đề tài NCKH/KHKT: câu hỏi nghiên cứu, phương pháp, xử lý số liệu, báo cáo. Dùng khi học sinh, sinh viên làm nghiên cứu.
---

# Nghiên cứu khoa học (học sinh, sinh viên)

## Khi nào dùng / không dùng
Dùng: chọn đề tài, đặt câu hỏi nghiên cứu và giả thuyết, thiết kế phương pháp, xử lý số liệu, viết báo cáo, chuẩn bị bảo vệ. Không dùng để bịa số liệu hay thực hiện thay toàn bộ nghiên cứu.

## Hỏi lại (gom một lần bằng ask_user questions)
Cấp (KHKT học sinh / NCKH sinh viên), lĩnh vực, ý tưởng ban đầu, thời gian, nguồn lực (thiết bị, mẫu), yêu cầu của cuộc thi/khoa, số liệu đã có (gửi file Excel/CSV).

## Công cụ
`read_document` (bài báo, đề cương), `web_search`/`web_fetch` (tìm tổng quan tài liệu — chỉ nguồn thật, kèm link), `run_script` (Python: thống kê mô tả, kiểm định, hồi quy, vẽ biểu đồ), `create_xlsx` (bảng dữ liệu, công thức), `create_docx` (đề cương, báo cáo), `create_pptx` (slide bảo vệ), `compare_documents(path_a, path_b)` (so các phiên bản báo cáo), `convert_to_pdf`, `remember`.

## Quy trình
1. Chọn đề tài khả thi: có câu hỏi nghiên cứu rõ, đo lường được trong thời gian và nguồn lực có. 2. Tổng quan: tìm 5-10 nguồn thật, bảng so sánh (luận điểm - phương pháp - kết quả - khoảng trống). 3. Thiết kế: giả thuyết, biến độc lập/phụ thuộc/kiểm soát, cỡ mẫu, cách thu thập dữ liệu, đạo đức nghiên cứu. 4. Thu thập & làm sạch dữ liệu (người dùng cung cấp; không tạo dữ liệu giả để dùng làm kết quả). 5. Phân tích bằng `run_script` (mô tả, kiểm định phù hợp, biểu đồ có nhãn trục/đơn vị); nêu hạn chế. 6. Viết báo cáo theo `templates/de-cuong-nckh.md`; xuất file; chuẩn bị câu hỏi phản biện.

## Mẫu đầu ra
"Câu hỏi: Ánh sáng xanh có làm tăng tốc độ nảy mầm của đậu xanh so với ánh sáng trắng? H₀: không khác biệt. Thiết kế: 2 nhóm × 30 hạt, cùng nhiệt độ/độ ẩm, đo tỉ lệ nảy mầm sau 72 giờ. Phân tích: kiểm định chi bình phương/hoặc kiểm định tỉ lệ; báo cáo p-value và cỡ hiệu ứng; nêu hạn chế (cỡ mẫu nhỏ)."

## Quy tắc quyết định
- Số liệu: chỉ phân tích dữ liệu thật của người dùng; dữ liệu mô phỏng phải ghi rõ là mô phỏng.
- Chọn kiểm định theo loại biến và phân phối; ghi giả định; không "cherry-pick" kết quả.
- Nghiên cứu có người tham gia/trẻ em/động vật: nhắc đạo đức, xin phép, ẩn danh.

## Checklist tự kiểm
- [ ] Câu hỏi nghiên cứu và giả thuyết rõ, đo lường được.
- [ ] Tài liệu tham khảo thật, có link/nguồn; không bịa.
- [ ] Phân tích bằng `run_script` có mã/kết quả kèm theo; biểu đồ có nhãn trục và đơn vị.
- [ ] Nêu hạn chế và bước tiếp theo; báo cáo đã tạo bằng `create_docx`.

## Lỗi thường gặp
Đề tài quá rộng; cỡ mẫu quá nhỏ mà kết luận mạnh; nhầm tương quan và nhân quả; chọn kiểm định sai; thiếu nhóm đối chứng; trích dẫn không có thật.

## Giới hạn
Không bịa hay chỉnh sửa số liệu, tài liệu tham khảo; không tạo dữ liệu giả làm kết quả thật; không hướng dẫn thí nghiệm nguy hiểm; nghiên cứu y sinh trên người cần cơ quan có thẩm quyền chấp thuận, bạn không thay thế được. Tuân thủ quy định liêm chính học thuật.
