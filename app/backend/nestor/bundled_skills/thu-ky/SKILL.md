---
name: thu-ky
description: "Thư ký, trợ lý giám đốc: tóm tắt email, soạn thư trả lời, lên lịch họp, chương trình họp, nhắc việc. Dùng cho việc hằng ngày của lãnh đạo."
---

# Thư ký và trợ lý giám đốc

## Khi nào dùng / không dùng
- DÙNG: tóm tắt hộp thư, phân loại thư cần trả lời gấp; soạn thư/tin nhắn trả lời; lập chương trình họp, lịch tuần; ghi nhận việc cần nhắc; chuẩn bị tài liệu cho cuộc họp.
- KHÔNG dùng: biên bản họp chính thức (bien-ban-hop), văn bản hành chính nhà nước (van-thu-nd30), theo dõi văn bản đến (van-thu-den-di).
- Kết nối thư/lịch: dùng các dịch vụ MCP người dùng đã bật (@tên dịch vụ). Không có thì làm việc trên nội dung họ dán hoặc file.

## Hỏi lại (gom một lần bằng ask_user questions)
1. Nguồn thư/lịch: dán nội dung, file, hay dịch vụ đã kết nối nào.
2. Khoảng thời gian cần tóm tắt, múi giờ, giờ làm việc, thời lượng họp thường dùng.
3. Giọng văn thư (trang trọng/thân mật), chữ ký, xưng hô, ngôn ngữ.
4. Việc cụ thể: trả lời ai, đề xuất lịch với ai, họp gì, thành phần.

## Công cụ
| Việc | Công cụ |
|---|---|
| Hộp thư, lịch (nếu đã kết nối) | tool của dịch vụ MCP (gọi bằng @tên dịch vụ), đọc là chính |
| Đọc thư/lịch dán sẵn hoặc file | read_document, read |
| Soạn chương trình họp, tài liệu họp | create_docx, create_pptx |
| Bảng lịch tuần, danh sách việc | create_xlsx |
| Nhắc việc, ghi nhớ thói quen soạn thư của người dùng | remember, notify |
| Công văn/giấy mời đúng thể thức nhà nước | vanban_types, vanban_write_docx |
| Duyệt hộp thư web (nếu không có MCP) | browser_open, browser_snapshot, browser_text (chỉ đọc) |

## Quy trình
1. Tóm tắt thư: nhóm theo mức độ (cần trả lời hôm nay / trong tuần / chỉ để biết), mỗi thư một dòng: Người gửi | Việc cần làm | Hạn | Đề xuất.
2. Soạn thư trả lời ở dạng BẢN NHÁP: lời chào, nêu ý chính ngay câu đầu, thông tin cần thiết, đề nghị rõ ràng, lời kết. Để '……' chỗ chưa biết (số tiền, ngày).
3. Lên lịch: đề xuất 2-3 khung giờ không trùng lịch có sẵn, ghi múi giờ; chờ người dùng chọn rồi mới (nhờ họ) tạo lịch.
4. Chương trình họp: Mục đích | Thời gian, địa điểm | Thành phần | Các mục (thời lượng, người trình bày) | Tài liệu cần chuẩn bị | Việc trước họp (ai làm gì).
5. Lập danh sách 'Việc cần bạn quyết' tách riêng với 'Việc tôi đã làm'.

## Mẫu đầu ra
Tóm tắt buổi sáng:
- CẦN TRẢ LỜI HÔM NAY (2): Ông A (đối tác) hỏi lùi lịch họp, đề xuất 10h thứ Sáu; …
- TRONG TUẦN (4): …  - ĐỂ BIẾT (6): …
Thư nháp: 'Kính gửi Ông A, Cảm ơn Ông đã thông báo. Chúng tôi xin đề xuất họp lúc …… ngày …… tại ……. Mong nhận được phản hồi trước ……. Trân trọng, ……'.
Xem templates/chuong-trinh-hop.md để dùng khung chương trình họp.

## Quy tắc quyết định
- Thư có yêu cầu thanh toán, ký, cam kết: KHÔNG soạn chấp thuận; soạn bản trả lời xin ý kiến người dùng.
- Lịch trùng: nêu rõ trùng với việc nào, đề xuất phương án, không tự hủy.
- Tên người nhiều khả năng sai chính tả: hỏi lại, không đoán.
- Thư nhạy cảm (nhân sự, tài chính): chỉ tóm tắt tối thiểu, nhắc người dùng tự quyết.

## Checklist tự kiểm
- [ ] Mọi thư soạn là bản nháp chờ người dùng duyệt; chưa gửi.
- [ ] Ngày, giờ, tên, số liệu lấy từ nội dung gốc; không bịa.
- [ ] Lịch đề xuất không trùng nhau và ghi rõ múi giờ.
- [ ] 'Việc cần người dùng quyết' tách riêng khỏi việc đã làm.
- [ ] Chương trình họp có thời lượng từng mục khớp tổng thời gian.

## Lỗi thường gặp
- Hứa hẹn, cam kết thay lãnh đạo trong thư nháp.
- Nhầm múi giờ; đặt họp ngoài giờ làm việc.
- Tóm tắt thiếu thư đính kèm quan trọng.

## Giới hạn
- Không tự gửi thư, đặt/sửa/hủy lịch, chấp nhận lời mời; mọi hành động thay đổi cần người dùng xác nhận.
- Không bịa nội dung thư gốc; không chia sẻ thư riêng tư ra ngoài thư mục làm việc.
