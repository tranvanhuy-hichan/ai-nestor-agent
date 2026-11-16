---
name: cv-phong-van
description: Viết CV chuyên nghiệp, thư xin việc và luyện phỏng vấn theo vị trí ứng tuyển. Dùng khi sinh viên hoặc người đi làm tìm việc.
---

# CV, thư xin việc, luyện phỏng vấn

## Khi nào dùng / không dùng
Dùng: CV (độ dài phù hợp hồ sơ), thư xin việc, trả lời phỏng vấn, đàm phán cơ bản. Không dùng để bịa kinh nghiệm hoặc giúp gian lận hồ sơ.

## Hỏi lại (gom một lần bằng ask_user questions)
Vị trí/ngành ứng tuyển và JD (dán hoặc gửi file), học vấn, kinh nghiệm/dự án/thực tập, kỹ năng, giải thưởng, ngôn ngữ CV (Việt/Anh), mẫu CV nếu có. Thiếu thông tin: để trống hoặc hỏi, không bịa.

## Công cụ
`read_cv_profile` (form gốc và ID từng mục), `read_document` (CV cũ, JD), `create_cv` (CV PDF và HTML theo mẫu mystore người dùng đã chọn), `create_docx` (chỉ thư xin việc), `convert_to_pdf` (xuất PDF để nộp), `web_search`/`web_fetch` (tìm hiểu công ty/ngành; nêu nguồn), `compare_documents(path_a, path_b)` (so CV cũ và mới), `remember` (hồ sơ để dùng lại).

## Quy trình
1. Phân tích JD: từ khóa kỹ năng, trách nhiệm chính. 2. Giữ đầy đủ thông tin người dùng nhập; chỉ sắp xếp ưu tiên theo JD, không tự loại bỏ. 3. Yêu cầu chọn mẫu CV trong form trước khi tạo; không tự chọn. Dùng create_cv với đúng template ID, chỉ dữ liệu thật, không sao chép dữ liệu mẫu trong ảnh xem trước. Viết nội dung theo `templates/cv-mot-trang.md`: Giới thiệu giữ đủ ý người dùng → Tất cả kinh nghiệm/dự án, giữ đủ ý chi tiết, không giới hạn số gạch đầu dòng → Học vấn → Kỹ năng → Giải thưởng. 4. Thư xin việc 3 đoạn (vì sao vị trí này → bạn mang gì → kêu gọi hành động), ≤ 250 từ. 5. Luyện phỏng vấn: hỏi thử 8-10 câu (giới thiệu bản thân, điểm mạnh yếu, tình huống STAR, lý do chọn công ty), nhận xét từng câu trả lời. 6. Xuất file và rà checklist.

## Mẫu đầu ra
Gạch đầu dòng tốt: "Xây dựng website bán hàng bằng React, tăng tốc độ tải trang 40% (từ 5s còn 3s), được 200 người dùng thử." Không tốt: "Làm website bán hàng."
Trả lời STAR: Tình huống - Nhiệm vụ - Hành động - Kết quả, 60-90 giây.

## Quy tắc quyết định
- Sinh viên chưa có kinh nghiệm: nhấn dự án học tập, hoạt động, kỹ năng chuyển đổi được.
- CV có thể dài hơn một trang. Ưu tiên đầy đủ thông tin liên quan, chữ dễ đọc và ngắt trang hợp lý; không ép thu nhỏ chữ hay bỏ kinh nghiệm chỉ để vừa một trang.
- Con số: chỉ dùng số người dùng cung cấp; không ước đoán thành sự thật.
- Ảnh/thông tin cá nhân nhạy cảm (số CCCD…): không đưa vào CV.

## Checklist tự kiểm
- [ ] CV theo mẫu, có thể nhiều trang, mỗi gạch đầu dòng có hành động + kết quả khi có dữ kiện.
- [ ] Từ khóa của JD xuất hiện tự nhiên.
- [ ] Không bịa kinh nghiệm, số liệu, bằng cấp.
- [ ] Thư xin việc ≤ 250 từ, đúng tên công ty/vị trí.
- [ ] CV đã tạo bằng `create_cv` đúng mẫu đã chọn (PDF và HTML); thư xin việc tạo bằng `create_docx`.

## Lỗi thường gặp
CV dài dòng, lặp ý; mô tả nhiệm vụ thay vì thành tích; sai tên công ty trong thư; lỗi chính tả; email thiếu chuyên nghiệp; bịa số liệu.

## Giới hạn
Không bịa kinh nghiệm, bằng cấp, số liệu; không giúp gian lận hồ sơ; không đưa thông tin nhạy cảm. Mọi nội dung là bản nháp để người dùng xác nhận trước khi nộp.


## Hồ sơ nhập theo mẫu
- Form `Thông tin cho mẫu CV đã chọn` gồm `template`, `data`, `skipped_sections`, `tone`.
- Ưu tiên thông tin trong form mới nhất. Chỉnh lời văn từng mục thành gọn, chủ động, tự tin, phù hợp JD.
- Được nhấn mạnh giá trị, chọn động từ mạnh và diễn đạt thuyết phục; không nâng khống chức danh, thâm niên, bằng cấp, kỹ năng hoặc kết quả.
- Giữ nguyên liên hệ, mốc thời gian và số liệu. Không lấy người mẫu trong ảnh preview vào CV thật.
- Tự soạn giới thiệu từ dữ kiện ở các mục khác nếu người dùng để trống phần giới thiệu.
- Mục được chọn bỏ qua phải truyền cho `create_cv` bằng `skipped_sections` (JSON chuỗi); không tự thêm trở lại.
- Mẫu có chỉ số nổi bật: dùng `highlights` với con số thật và ý nghĩa. Mẫu có sở thích: dùng `interests`.
- Nếu có `photo_path`, giữ đường dẫn đó trong data để công cụ dùng đúng ảnh chân dung đã tải lên.
- Thiếu dữ kiện quan trọng thì hỏi gộp một lần. Sau xuất file, tóm tắt các chỉnh sửa để người dùng kiểm và yêu cầu sửa tiếp.

- Không tự tóm tắt, bỏ mục, cắt ý để CV ngắn hơn. Giữ ID từng bản ghi. Muốn rút gọn phải hỏi trước. Đọc kết quả đối chiếu của create_cv và báo rõ những phần phải giữ nguyên từ form gốc.

- Phải thực sự viết lại câu chữ thô thành nội dung chuyên nghiệp, không chỉ sao chép vào mẫu. Giữ đầy đủ ý nhưng được đổi câu, sửa chính tả và sắp xếp lại. Nếu create_cv báo bản biên tập thiếu, đọc lại form và hoàn thiện bản viết lại trước khi xuất; không trả người dùng bản thô.
