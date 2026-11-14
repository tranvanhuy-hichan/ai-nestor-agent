---
name: nhan-su
description: "Hành chính nhân sự: tin tuyển dụng, mô tả công việc, sinh hàng loạt hợp đồng/quyết định từ mẫu Word + Excel, tài liệu nhân viên mới. Dùng khi cần văn bản nhân sự."
---

# Hành chính - Nhân sự

## Khi nào dùng / không dùng
- DÙNG: soạn tin tuyển dụng, mô tả công việc (JD), thư mời nhận việc; sinh hàng trăm hợp đồng/quyết định/giấy xác nhận/thông báo từ MỘT mẫu Word và danh sách Excel; soạn quy chế, nội quy, tài liệu onboarding; biểu mẫu điền được.
- KHÔNG dùng: quyết định tuyển/sa thải/kỷ luật/mức lương (người có thẩm quyền quyết); văn bản hành chính nhà nước (van-thu-nd30); tính lương chi tiết có thuế (kế toán).
- Dữ liệu nhân viên là dữ liệu cá nhân: dùng tối thiểu cần thiết, không đưa ra ngoài thư mục làm việc.

## Hỏi lại (gom một lần bằng ask_user questions)
1. Việc cần làm: tin tuyển dụng, JD, hợp đồng hàng loạt, quy chế, onboarding.
2. Với hàng loạt: file mẫu .docx (có chỗ trống dạng {{ten_truong}}), file danh sách .xlsx/.csv (mỗi dòng một người), cột nào dùng đặt tên file.
3. Thông tin pháp lý cố định của công ty (tên, MST, địa chỉ, người đại diện) và chính sách (thử việc, lương, phụ cấp) do người dùng cung cấp.
4. Với tuyển dụng: vị trí, số lượng, yêu cầu, quyền lợi, hạn nộp, kênh đăng.

## Công cụ
| Việc | Công cụ |
|---|---|
| Sinh hàng loạt tài liệu từ mẫu Word và dữ liệu | docx_fill_template(template_path, data, data_path, output_dir, name_field) |
| Đọc mẫu, danh sách | read_document, read |
| Kiểm tra danh sách (thiếu, trùng, sai định dạng) | excel_audit(path), run_script |
| Soạn tin tuyển dụng, JD, quy chế, tài liệu | create_docx |
| Biểu mẫu điền được, bảng theo dõi | create_xlsx, create_docx |
| Ảnh minh họa tin tuyển dụng (nếu cần) | generate_image |
| Xuất PDF từng file hoặc cả bộ | convert_to_pdf(path) |

## Quy trình sinh hàng loạt (hợp đồng, quyết định)
1. Đọc mẫu bằng read_document; liệt kê các chỗ điền (placeholder). Mẫu chưa có placeholder thì đề xuất vị trí và nhờ người dùng xác nhận mẫu có placeholder (không tự sửa mẫu gốc).
2. Kiểm tra danh sách bằng excel_audit: thiếu trường bắt buộc, ngày sai định dạng, số điện thoại/CMND/CCCD lạ, dòng trùng. Liệt kê lỗi, KHÔNG sinh file cho dòng lỗi cho đến khi người dùng sửa hoặc xác nhận bỏ qua.
3. Chạy thử: docx_fill_template với MỘT dòng, mở kết quả bằng read_document kiểm tra từng chỗ điền.
4. Chạy toàn bộ: docx_fill_template(template_path, data_path, output_dir, name_field). Đặt tên file có mã/họ tên không dấu, tránh trùng.
5. Đối chiếu: số file sinh = số dòng hợp lệ; không còn placeholder chưa điền trong file mẫu mới (đọc ngẫu nhiên 3 file); danh sách lỗi riêng.
6. Báo số file, lỗi, dòng bị bỏ qua; nhắc điều khoản cần người có thẩm quyền duyệt trước khi ký.

## Quy trình tuyển dụng, JD, onboarding
- Tin tuyển dụng: tiêu đề vị trí; giới thiệu ngắn công ty; mô tả công việc (5-7 gạch); yêu cầu (bắt buộc / ưu tiên); quyền lợi (chỉ ghi điều người dùng cung cấp, KHÔNG bịa mức lương/phúc lợi); cách ứng tuyển, hạn nộp.
- JD: vị trí, báo cáo cho ai, mục đích, trách nhiệm chính, yêu cầu năng lực, KPI (nếu người dùng nêu).
- Onboarding: ngày đầu, người tiếp đón, quy định chính, hệ thống cần truy cập, lộ trình 30-60-90 ngày, liên hệ.
- Quy chế, nội quy: soạn bản nháp từ chính sách người dùng cung cấp; đánh dấu điều khoản pháp lý quan trọng 'cần kiểm chứng/cần pháp chế duyệt'.

## Mẫu đầu ra
- Hàng loạt: output_dir/ chứa HD-001-nguyen-van-a.docx ...; kèm bảng 'ket-qua.xlsx' (Dòng | Họ tên | File | Trạng thái).
- Placeholder đề xuất: {{ho_ten}}, {{ngay_sinh}}, {{cccd}}, {{chuc_vu}}, {{luong}}, {{ngay_bat_dau}}.
- Ví dụ: 40 dòng danh sách, 2 dòng thiếu CCCD → sinh 38 file; báo lỗi dòng 7 và 19.

## Quy tắc quyết định
- Số tiền (lương, thưởng, phụ cấp), ngày nghỉ, thời hạn: chỉ lấy từ dữ liệu người dùng; thiếu thì lỗi, không điền mặc định.
- Điều khoản pháp luật lao động (thử việc, bảo hiểm, chấm dứt): chỉ nêu khi có trong mẫu của công ty; thêm mới thì 'cần kiểm chứng'.
- Thông tin cá nhân không cần cho văn bản (ngày sinh trong tin tuyển dụng...): không đưa vào.

## Checklist tự kiểm
- [ ] Mọi con số lương, thưởng, ngày nghỉ do người dùng cung cấp.
- [ ] Hàng loạt: số file = số dòng hợp lệ; lỗi được liệt kê; mở ít nhất 3 file kiểm tra không còn placeholder.
- [ ] Đã chạy thử một dòng trước khi chạy toàn bộ.
- [ ] Sản phẩm gửi rộng không có thông tin cá nhân thừa.
- [ ] Điều khoản pháp lý quan trọng được đánh dấu cần xác nhận.

## Lỗi thường gặp
- Chạy hàng loạt không kiểm danh sách, sinh nhầm lương/ngày.
- Placeholder bị tách trong nhiều run của Word nên không điền được (docx_fill_template sẽ báo thiếu; nhờ người dùng gõ lại placeholder liền mạch).
- Lộ thông tin cá nhân của người khác trong file chung.

## Giới hạn
- Không quyết định tuyển, kỷ luật, mức lương; không ký, không gửi hợp đồng cho nhân viên.
- Không bịa số tiền, ngày, điều khoản. Dữ liệu cá nhân chỉ xử lý trong thư mục làm việc.
