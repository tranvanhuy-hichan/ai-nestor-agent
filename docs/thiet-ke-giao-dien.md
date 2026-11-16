# Thiết kế giao diện cho người dùng phổ thông

Nestor có hai giao diện trong cùng một ứng dụng, đổi bằng nút **Nâng cao / Đơn giản** ở cuối thanh bên (lựa chọn lưu trong `localStorage`, khóa `ui-mode`, mặc định là *Đơn giản*).

## Người dùng mục tiêu

Cán bộ, chuyên viên, nhân viên văn phòng: giỏi nghiệp vụ, không rành kỹ thuật. Họ nghĩ theo **việc cần xong** ("soạn tờ trình", "tổng hợp báo cáo 12 phường"), không nghĩ theo công cụ (model, token, MCP). Brochure COffice AI nhắm đúng nhóm này; các nguyên tắc dưới đây rút từ đó.

## Nguyên tắc

1. **Việc trước, công cụ sau.** Trang chủ là một ô lớn "Bạn muốn tôi giúp việc gì?", không phải bảng thống kê.
2. **Trợ lý là thẻ, không phải cấu hình.** Chọn "Văn thư", "Kế toán"... thay vì chọn model hay viết prompt. Mỗi thẻ có mô tả một dòng và vài câu mẫu bấm là chạy. Chia nhóm *Cơ quan nhà nước* / *Doanh nghiệp*.
3. **Kết quả là file thật.** Hiện danh sách `.docx/.xlsx/.pptx/.pdf` gần đây kèm nút *Tải về*; người dùng không phải đọc văn bản trong khung chat rồi tự chép.
4. **Từ ngữ đời thường.** Không dùng: MCP, token, provider, workspace, shell, sandbox. Dùng: "ứng dụng bên ngoài", "tài khoản AI", "chạy một chương trình trên máy bạn".
5. **Xin phép rõ ràng với việc có rủi ro.** Gửi, ký, nộp, xóa, ghi đè luôn hỏi bằng câu hoàn chỉnh ("Trợ lý xin phép lưu hoặc sửa một file. Bạn có đồng ý không?") và nút *Đồng ý / Không đồng ý*; chi tiết kỹ thuật gập trong "Xem chi tiết". Chế độ Đơn giản mặc định dùng quyền "Hỏi trước".
6. **Càng làm càng giỏi.** Sau một việc tốt, nút *Lưu thành kỹ năng* (cách làm) và *Ghi nhớ quy tắc* (yêu cầu cố định) để lần sau chỉ cần nói "làm như lần trước".
7. **Làm cả khi vắng mặt.** Lịch tự động và nhận việc qua Zalo/Telegram là tính năng hàng đầu, nằm ngay trong Cài đặt đơn giản, không phải trong trang "Kết nối".
8. **Ít mục, mỗi mục một mục đích.** Thanh bên đơn giản chỉ có 6 mục.
9. **Mở dần theo nhu cầu (progressive disclosure).** Mọi thứ phức tạp vẫn còn, nằm sau nút *Nâng cao*; không bao giờ mất tính năng, chỉ ẩn.

## Hai chế độ

| | Đơn giản | Nâng cao |
|---|---|---|
| Thanh bên | Trợ lý · Việc đã làm · Lịch tự động · Tài liệu · Kỹ năng của tôi · Cài đặt | Toàn bộ như trước (Mô hình AI, Kết nối, Tiện ích, Thống kê, Tác vụ...) |
| Trang chủ | Ô giao việc + thẻ trợ lý + kết quả gần đây | Bảng tổng quan, gợi ý cấu hình |
| Chat | Không có terminal/git/workspace/chọn model/quyền; có tiến độ tổ công tác, lưu kỹ năng | Đầy đủ |
| Cài đặt | Ngôn ngữ, tài khoản AI, Zalo, Telegram | Tính năng, bảo mật, sao lưu... |
| Trang chỉ dành cho Nâng cao | Tự chuyển về trang chủ | Truy cập bình thường |

## Kỹ thuật

- Trạng thái: [`lib/uiMode.ts`](../app/frontend/src/lib/uiMode.ts) (`useUiMode`, `setUiMode`).
- Danh sách trợ lý: `GET /api/assistants` → `{id, name, icon, group, description, starters[]}`; khi lỗi dùng danh sách dự phòng trong [`lib/assistants.ts`](../app/frontend/src/lib/assistants.ts). Chat gửi thêm trường `assistant` trong `POST /api/chat`.
- Lưu kỹ năng/quy tắc: `POST /api/sessions/{id}/distill {kind: 'skill'|'rule'}`. Tiến độ tổ công tác: `GET /api/teams/{id}/status` (không có thì không hiện).
- Zalo: `GET/PUT /api/channels/zalo` (`enabled`, `token`).
- Chuỗi mới luôn bọc `t()` và có bản Anh trong `src/i18n/en/simple.ts`.

## Kiểm thử với người dùng thật

Mời 3-5 cán bộ văn phòng, giao 4 việc không hướng dẫn: soạn một tờ trình, tìm lại file hôm qua, cho phép/từ chối một yêu cầu xin phép, kết nối Zalo. Đo: có xong không, mất bao lâu, từ nào làm họ khựng lại. Sửa từ ngữ trước khi sửa bố cục.
