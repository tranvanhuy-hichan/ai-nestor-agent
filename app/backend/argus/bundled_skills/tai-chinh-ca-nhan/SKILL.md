---
name: tai-chinh-ca-nhan
description: Lập ngân sách, bảng theo dõi chi tiêu Excel và kế hoạch tiết kiệm; không tư vấn đầu tư cụ thể. Dùng khi người dùng quản lý tiền cá nhân.
---

# Tài chính cá nhân: ngân sách, theo dõi chi tiêu, tiết kiệm

## Khi nào dùng / không dùng
Dùng: lập ngân sách tháng, bảng theo dõi chi tiêu, phân loại chi tiêu từ sao kê/ghi chép, mục tiêu tiết kiệm, kế hoạch trả nợ. Không dùng để khuyên mua cổ phiếu/coin/bảo hiểm cụ thể hay dự báo lợi nhuận.

## Hỏi lại (gom một lần bằng ask_user questions)
Thu nhập ròng hằng tháng, khoản cố định (thuê nhà, điện nước, trả nợ), mục tiêu (quỹ khẩn cấp, mua xe…), thời hạn, có file sao kê/chi tiêu không (gửi Excel/CSV). Không yêu cầu số tài khoản, mật khẩu, mã OTP.

## Công cụ
`create_xlsx` (ngân sách, bảng chi tiêu theo tháng, công thức SUM/SUMIF, biểu đồ ngân sách), `excel_audit(path)` (kiểm tra bảng chi tiêu/ngân sách: lỗi công thức, ô trống, tổng sai, mục trùng — báo từng lỗi và cách sửa), `read_document` (đọc sao kê CSV/Excel), `run_script` (phân loại giao dịch hàng loạt, tính lãi/kỳ trả nợ), `create_docx` (báo cáo ngắn), `remember`.

## Quy trình
1. Thu thập thu nhập và chi tiêu thật (người dùng cung cấp). 2. Phân loại: nhu cầu thiết yếu / mong muốn / tiết kiệm-trả nợ (gợi ý ban đầu 50/30/20, điều chỉnh theo hoàn cảnh, ghi rõ đây chỉ là gợi ý). 3. Lập bảng Excel: sheet Ngân sách, sheet Chi tiêu (Ngày | Mục | Số tiền | Ghi chú), sheet Tổng hợp (SUMIF theo mục, % so với ngân sách) — xem `templates/ngan-sach-thang.md`. 4. Chạy `excel_audit` trên file vừa tạo hoặc file người dùng gửi; sửa lỗi. 5. Đề xuất 2-3 hành động cắt giảm cụ thể từ dữ liệu thật. 6. Kế hoạch tiết kiệm: số tiền/tháng × số tháng = mục tiêu; kiểm tra khả thi.

## Mẫu đầu ra
"Thu nhập 15.000.000đ. Thiết yếu 7.500.000đ (50%), mong muốn 4.500.000đ (30%), tiết kiệm 3.000.000đ (20%). Mục tiêu quỹ khẩn cấp 45.000.000đ (3 tháng chi tiêu) → 15 tháng nếu gửi đều 3.000.000đ. Kiểm tra: tổng ba nhóm = 15.000.000đ ✓. Gợi ý: khoản 'ăn ngoài' đang 2,4 triệu, thử đặt trần 1,8 triệu."

## Quy tắc quyết định
- Số liệu luôn lấy từ người dùng; không đoán thu nhập, lãi suất hiện hành (nếu cần, tra nguồn chính thức và ghi ngày).
- Có nợ lãi cao: ưu tiên trả nợ trước khi tăng đầu tư.
- Câu hỏi "nên mua/bán gì": từ chối tư vấn cụ thể, nêu nguyên tắc chung (đa dạng hóa, quỹ khẩn cấp, chỉ dùng tiền nhàn rỗi) và khuyên tham khảo chuyên gia được cấp phép.

## Checklist tự kiểm
- [ ] Tổng các nhóm ngân sách = thu nhập (hoặc ghi chênh lệch).
- [ ] Công thức Excel đúng (đã chạy `excel_audit`, không còn lỗi).
- [ ] Mục tiêu tiết kiệm khả thi theo thời hạn.
- [ ] Không có khuyến nghị đầu tư cụ thể; không yêu cầu thông tin tài khoản.

## Lỗi thường gặp
Quên khoản chi không thường xuyên (bảo hiểm, học phí); công thức tham chiếu sai ô; ngân sách không có "quỹ dự phòng"; đặt mục tiêu quá cao; tính lãi sai kỳ.

## Giới hạn
Không tư vấn đầu tư chứng khoán/tiền số/bảo hiểm cụ thể, không hứa lợi nhuận; không yêu cầu hay lưu số tài khoản, mật khẩu, OTP; đây là công cụ hỗ trợ lập kế hoạch, không thay thế tư vấn tài chính chuyên nghiệp.
