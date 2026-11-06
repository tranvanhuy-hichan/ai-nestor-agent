---
name: thuyet-trinh-slide
description: Làm slide PowerPoint gọn, kịch bản thuyết trình và câu hỏi phản biện cho bảo vệ đồ án, báo cáo. Dùng khi cần bài thuyết trình.
---

# Slide và thuyết trình

## Khi nào dùng
Làm bộ slide cho bảo vệ đồ án, báo cáo nhóm, pitch, bài giảng; viết kịch bản nói và luyện câu hỏi phản biện.

## Hỏi lại (gom một lần bằng ask_user questions)
Đối tượng người nghe, thời lượng (5/10/15 phút), mục đích (thuyết phục/báo cáo/bảo vệ), nội dung gốc (gửi file), phong cách (trang trọng/trẻ trung), mẫu slide của trường/công ty.

## Công cụ
`read_document` (đọc báo cáo/đồ án nguồn), `create_pptx` (xuất slide, ghi chú diễn giả trong `notes`), `generate_image` (ảnh minh họa khi có provider; nêu giả định bản quyền), `create_docx` (kịch bản nói, bảng câu hỏi phản biện), `run_script` (đếm số slide/thời gian), `convert_to_pdf` (xuất PDF để nộp/in).

## Quy trình
1. Xác định thông điệp chính (một câu) và 3 ý hỗ trợ. 2. Tính số slide: ≈ 1 slide/phút (5 phút ≈ 5-7 slide; 15 phút ≈ 12-15). 3. Cấu trúc: bìa → vấn đề/bối cảnh → mục tiêu → giải pháp/phương pháp → kết quả (số liệu, biểu đồ) → kết luận/đề xuất → cảm ơn/Q&A. 4. Mỗi slide một ý, tiêu đề là câu khẳng định, ≤ 6 dòng, chữ ≥ 24 pt. 5. Viết ghi chú diễn giả cho từng slide (lời nói + thời gian). 6. Đặt 5-8 câu hỏi phản biện dễ gặp + gợi ý trả lời. 7. Xuất `create_pptx` và rà checklist.

## Mẫu đầu ra
Slide 4 (bảo vệ đồ án quản lý thư viện): Tiêu đề "Hệ thống rút ngắn 70% thời gian mượn sách". Nội dung: sơ đồ 3 bước + 1 con số. Ghi chú: "Nói 45 giây: trước đây thủ thư nhập tay…, giờ quét mã…; nhấn mạnh số liệu thử nghiệm với 50 lượt mượn."
Câu hỏi phản biện mẫu: "Dữ liệu 50 lượt có đủ đại diện không?" → trả lời: nêu giới hạn mẫu và kế hoạch mở rộng.

## Quy tắc quyết định
- Quá nhiều nội dung: ưu tiên kết quả/thông điệp, đẩy chi tiết vào phụ lục.
- Dữ liệu/biểu đồ: nêu nguồn và đơn vị; không bịa số liệu.
- Thời lượng hạn chế: bỏ slide phụ, không tăng cỡ chữ nhỏ lại.

## Quy tắc thiết kế slide nhanh
Chữ nội dung ≥ 24 pt, tiêu đề ≥ 32 pt; tối đa 2 phông, 3 màu; tương phản chữ - nền cao; mỗi biểu đồ một thông điệp, ghi nguồn và đơn vị dưới biểu đồ; ảnh rõ nét, đúng bản quyền; số trang ở góc; slide kết nêu đúng một lời kêu gọi hành động.

## Luyện nói và phản biện
Luyện theo thời lượng thật, bấm giờ từng slide; nói ý chứ không đọc nguyên chữ; chuẩn bị 3 câu trả lời "cửa sau" cho câu hỏi khó (nêu hạn chế thẳng thắn, đưa kế hoạch cải tiến). Nếu dữ liệu chưa đủ chắc, nói rõ "kết quả bước đầu" thay vì khẳng định mạnh.

## Checklist tự kiểm
- [ ] Số slide phù hợp thời lượng; mỗi slide một ý, ≤ 6 dòng.
- [ ] Có ghi chú diễn giả mọi slide chính.
- [ ] Có 5+ câu hỏi phản biện kèm gợi ý trả lời.
- [ ] Số liệu có nguồn; file đã tạo bằng `create_pptx`.

## Lỗi thường gặp
Slide dày chữ; đọc nguyên slide; không có thông điệp chính; biểu đồ không nêu nguồn; vượt giờ; font/màu khó đọc.

## Giới hạn
Không bịa số liệu, nguồn, kết quả nghiên cứu; hình ảnh cần đúng bản quyền; không viết hộ nội dung khoa học chưa có dữ liệu thật của người dùng.
