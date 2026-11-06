---
name: cv-phong-van
description: Viết CV một trang, thư xin việc và luyện phỏng vấn theo vị trí ứng tuyển. Dùng khi sinh viên hoặc người đi làm tìm việc.
---

# CV, thư xin việc, luyện phỏng vấn

## Khi nào dùng / không dùng
Dùng: CV (một trang), thư xin việc, trả lời phỏng vấn, đàm phán cơ bản. Không dùng để bịa kinh nghiệm hoặc giúp gian lận hồ sơ.

## Hỏi lại (gom một lần bằng ask_user questions)
Vị trí/ngành ứng tuyển và JD (dán hoặc gửi file), học vấn, kinh nghiệm/dự án/thực tập, kỹ năng, giải thưởng, ngôn ngữ CV (Việt/Anh), mẫu CV nếu có. Thiếu thông tin: để trống hoặc hỏi, không bịa.

## Công cụ
`read_document` (CV cũ, JD), `create_docx` (CV, thư xin việc), `convert_to_pdf` (xuất PDF để nộp), `web_search`/`web_fetch` (tìm hiểu công ty/ngành; nêu nguồn), `compare_documents(path_a, path_b)` (so CV cũ và mới), `remember` (hồ sơ để dùng lại).

## Quy trình
1. Phân tích JD: từ khóa kỹ năng, trách nhiệm chính. 2. Chọn thông tin phù hợp nhất từ hồ sơ của người dùng. 3. Viết CV theo `templates/cv-mot-trang.md`: Tóm tắt 2-3 dòng → Kinh nghiệm/dự án (mỗi mục 2-4 gạch đầu dòng kiểu hành động + kết quả đo được) → Học vấn → Kỹ năng → Giải thưởng. 4. Thư xin việc 3 đoạn (vì sao vị trí này → bạn mang gì → kêu gọi hành động), ≤ 250 từ. 5. Luyện phỏng vấn: hỏi thử 8-10 câu (giới thiệu bản thân, điểm mạnh yếu, tình huống STAR, lý do chọn công ty), nhận xét từng câu trả lời. 6. Xuất file và rà checklist.

## Mẫu đầu ra
Gạch đầu dòng tốt: "Xây dựng website bán hàng bằng React, tăng tốc độ tải trang 40% (từ 5s còn 3s), được 200 người dùng thử." Không tốt: "Làm website bán hàng."
Trả lời STAR: Tình huống - Nhiệm vụ - Hành động - Kết quả, 60-90 giây.

## Quy tắc quyết định
- Sinh viên chưa có kinh nghiệm: nhấn dự án học tập, hoạt động, kỹ năng chuyển đổi được.
- CV một trang cho dưới 5 năm kinh nghiệm.
- Con số: chỉ dùng số người dùng cung cấp; không ước đoán thành sự thật.
- Ảnh/thông tin cá nhân nhạy cảm (số CCCD…): không đưa vào CV.

## Checklist tự kiểm
- [ ] CV một trang, mỗi gạch đầu dòng có hành động + kết quả khi có dữ kiện.
- [ ] Từ khóa của JD xuất hiện tự nhiên.
- [ ] Không bịa kinh nghiệm, số liệu, bằng cấp.
- [ ] Thư xin việc ≤ 250 từ, đúng tên công ty/vị trí.
- [ ] File đã tạo bằng `create_docx` (PDF qua `convert_to_pdf` nếu cần).

## Lỗi thường gặp
CV dài; mô tả nhiệm vụ thay vì thành tích; sai tên công ty trong thư; lỗi chính tả; email thiếu chuyên nghiệp; bịa số liệu.

## Giới hạn
Không bịa kinh nghiệm, bằng cấp, số liệu; không giúp gian lận hồ sơ; không đưa thông tin nhạy cảm. Mọi nội dung là bản nháp để người dùng xác nhận trước khi nộp.
