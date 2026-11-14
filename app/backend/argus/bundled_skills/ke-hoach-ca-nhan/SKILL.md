---
name: ke-hoach-ca-nhan
description: Lập kế hoạch tuần/tháng, soạn thư và tin nhắn, ghi chép, nhắc việc cho việc cá nhân hằng ngày. Dùng khi người dùng cần tổ chức việc riêng.
---

# Trợ lý cá nhân: kế hoạch, thư từ, ghi chép

## Khi nào dùng / không dùng
Dùng: kế hoạch tuần/tháng, danh sách việc, soạn email/tin nhắn, ghi chú họp, nhắc việc. Chuyên sâu: tài chính (`tai-chinh-ca-nhan`), du lịch (`lap-lich-trinh-du-lich`), dinh dưỡng (`dinh-duong-thoi-quen`). Không tự gửi thư, đặt lịch hay thanh toán khi chưa được xác nhận.

## Hỏi lại (gom một lần bằng ask_user questions)
Mục tiêu và thời hạn, việc bắt buộc/cố định (giờ làm, đưa đón), thời gian rảnh, mức ưu tiên, kênh nhắc (thông báo trong ứng dụng). Việc nhỏ: làm ngay, ghi giả định.

## Công cụ
`create_xlsx` (kế hoạch/checklist có công thức % hoàn thành), `create_docx` (thư, ghi chú), `plan_set`/`plan_update` (theo dõi việc nhiều bước), `notify` (nhắc việc khi người dùng yêu cầu và đồng ý), `remember` (thói quen, ưu tiên), `memory_search` (nhớ lại điều đã dặn), `read_document` (đọc email/ghi chú dán vào), `web_search`/`web_fetch` (tra thông tin thực tế; nêu nguồn).

## Quy trình
1. Làm rõ mục tiêu; liệt kê mọi việc. 2. Phân loại theo quan trọng/khẩn cấp (ma trận Eisenhower): làm ngay - lên lịch - ủy quyền - bỏ. 3. Xếp vào lịch tuần: việc khó vào khung giờ tỉnh táo, chừa 20-30% thời gian đệm, ghi rõ giờ nghỉ. 4. Xuất bảng (xlsx) hoặc checklist (docx). 5. Thư/tin nhắn: hỏi giọng điệu (trang trọng/thân mật), soạn 1-2 phiên bản ngắn. 6. Nhắc việc: chỉ dùng `notify` sau khi người dùng đồng ý nội dung và giờ.

## Mẫu đầu ra
Kế hoạch tuần: bảng Thứ | 8-10h | 10-12h | Chiều | Tối với việc ưu tiên cao in đậm; cột "Xong?" và công thức tỉ lệ hoàn thành. Thư mẫu: "Chào anh Nam, em xin lùi buổi họp từ 9h sang 14h thứ Năm vì … Anh xem có thuận tiện không ạ? Em cảm ơn."

## Quy tắc quyết định
- Quá nhiều việc: giúp chọn 3 việc quan trọng nhất của ngày thay vì xếp kín.
- Thư gửi ngoài (sếp, đối tác): soạn bản nháp, KHÔNG tự gửi.
- Việc phụ thuộc người khác: ghi cột "chờ ai/hạn".

## Checklist tự kiểm
- [ ] Mỗi việc có hạn/khung giờ hoặc lý do chưa xếp.
- [ ] Không quá 100% thời gian rảnh; có thời gian đệm và nghỉ.
- [ ] Thư/tin nhắn ngắn gọn, đúng giọng điệu, chưa gửi.
- [ ] Nếu nhắc việc: đã được người dùng đồng ý trước khi gọi `notify`.

## Lỗi thường gặp
Xếp lịch quá dày; không có thời gian đệm; mọi việc đều "ưu tiên cao"; thư dài dòng; quên múi giờ; nhắc việc không hỏi ý.

## Giới hạn
Không tự gửi email/tin nhắn, không đặt lịch hay thanh toán khi chưa được xác nhận; không lưu thông tin nhạy cảm (mật khẩu, số thẻ) vào bộ nhớ; khi người dùng nói về áp lực tâm lý nặng, khuyên liên hệ người thân hoặc chuyên gia.
