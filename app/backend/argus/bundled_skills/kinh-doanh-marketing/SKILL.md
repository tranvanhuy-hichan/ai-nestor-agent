---
name: kinh-doanh-marketing
description: "Hồ sơ năng lực, pitch deck, báo giá, thư chào hàng, bài đăng truyền thông từ dữ kiện thật của công ty. Dùng cho bán hàng và marketing."
---

# Kinh doanh - Marketing

## Khi nào dùng / không dùng
- DÙNG: slide giới thiệu công ty/sản phẩm, pitch deck gọi vốn, hồ sơ năng lực, báo giá, thư chào hàng, kế hoạch marketing, lịch nội dung, bài đăng mạng xã hội, email chiến dịch.
- KHÔNG dùng: hợp đồng (phap-che), phân tích tài chính chi tiết (ke-toan), thiết kế đồ họa phức tạp ngoài khả năng (nói thẳng).
- Nội dung chỉ dựa trên dữ kiện thật người dùng cung cấp.

## Hỏi lại (gom một lần bằng ask_user questions)
1. Mục đích và người nhận (khách hàng, nhà đầu tư, đối tác, công chúng), kênh/định dạng.
2. Dữ kiện thật: tên công ty, lĩnh vực, sản phẩm/dịch vụ, khách hàng tiêu biểu (được phép nêu), số liệu, giải thưởng, đội ngũ, liên hệ.
3. Giọng điệu, màu sắc/nhận diện (nếu có), độ dài (số slide), ngôn ngữ.
4. Báo giá: hạng mục, đơn giá, số lượng, điều kiện thanh toán, hiệu lực, người ký.

## Công cụ
| Việc | Công cụ |
|---|---|
| Slide, pitch deck | create_pptx (slides JSON: title, bullets, notes) |
| Hồ sơ năng lực, thư chào hàng, kế hoạch | create_docx |
| Báo giá, bảng giá, lịch nội dung | create_xlsx (tổng bằng công thức) |
| Ảnh minh họa, banner | generate_image (mô tả cụ thể, tránh logo/chữ giả) |
| Tìm số liệu thị trường, đối thủ (công khai) | web_search, web_fetch (ghi nguồn, ngày) |
| Đọc tài liệu công ty | read_document, kb_search |
| Tính toán, phân tích dữ liệu bán hàng | run_script |
| Xuất PDF | convert_to_pdf(path) |

## Quy trình
1. Đọc tài liệu/kho công ty; liệt kê dữ kiện có và thiếu. Dữ kiện thiếu: hỏi hoặc để '……'.
2. Chọn khung (xem Mẫu). Mỗi slide MỘT thông điệp: tiêu đề là kết luận, 3-5 gạch ngắn, ghi chú diễn giả trong notes.
3. Số liệu thị trường/đối thủ lấy từ nguồn công khai có dẫn nguồn và ngày; không có nguồn thì không đưa.
4. Báo giá: bảng hạng mục có thành tiền, VAT (nếu người dùng nêu), tổng bằng công thức, điều kiện, hiệu lực; không tự giảm giá hay hứa khuyến mãi.
5. Bài đăng: 3 phương án (ngắn, kể chuyện, thông tin), kèm hashtag/CTA phù hợp kênh; nhắc kiểm duyệt quy định quảng cáo.
6. Tạo file; tự đọc lại (read_document) kiểm tra số liệu và chính tả; báo danh sách dữ kiện còn thiếu và điểm cần xác nhận.

## Mẫu đầu ra
- Pitch deck 10 slide: 1 Bìa; 2 Vấn đề; 3 Giải pháp; 4 Sản phẩm/Demo; 5 Thị trường (có nguồn); 6 Mô hình kinh doanh; 7 Traction (số liệu thật); 8 Đội ngũ; 9 Kế hoạch/Lộ trình; 10 Kêu gọi (số tiền, mục đích, liên hệ).
- Hồ sơ năng lực: Giới thiệu; Lĩnh vực hoạt động; Năng lực nhân sự; Dự án tiêu biểu (có chứng từ); Chứng chỉ; Liên hệ.
- Thư chào hàng: lời chào; vấn đề của khách; giải pháp ngắn; bằng chứng; đề nghị gặp (ngày giờ gợi ý); chữ ký.
- Ví dụ: 'Slide 7: Doanh thu tăng 3 lần trong 12 tháng' chỉ được viết khi người dùng cung cấp số; nếu không: 'Doanh thu …… (cần số liệu)'.

## Quy tắc quyết định
- Khẳng định 'số 1', 'duy nhất', 'tốt nhất', so sánh trực tiếp đối thủ: chỉ khi có bằng chứng người dùng đưa; còn lại bỏ hoặc đánh dấu 'cần xác nhận'.
- Tên khách hàng/logo: chỉ dùng khi người dùng nói được phép nêu.
- Giá và khuyến mãi: chỉ theo bảng giá người dùng đưa.
- Ảnh tạo bằng generate_image: không dùng như ảnh thật của sản phẩm/người thật.

## Checklist tự kiểm
- [ ] Không có số liệu, khách hàng, giải thưởng nào ngoài dữ kiện người dùng đưa.
- [ ] Mỗi slide một thông điệp; file .pptx đã tạo và mở lại đọc được.
- [ ] Báo giá có hiệu lực, điều kiện, tổng bằng công thức.
- [ ] Cam kết và so sánh đối thủ đã được đánh dấu cần xác nhận.
- [ ] Số liệu thị trường có nguồn và ngày.

## Lỗi thường gặp
- Bịa traction, khách hàng, giải thưởng để slide đẹp.
- Slide nhiều chữ; không có thông điệp.
- Ảnh AI chứa chữ sai chính tả; dùng như ảnh thật.

## Giới hạn
- Không gửi thư chào hàng, không đăng bài, không thanh toán/chuyển khoản.
- Không bịa số liệu, cam kết; không xâm phạm bản quyền ảnh/nhạc/logo. Không nêu thông tin bảo mật của công ty khi chưa được phép.
