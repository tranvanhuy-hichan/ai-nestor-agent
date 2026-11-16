---
name: giao-an-gdpt-2018
description: Soạn giáo án (kế hoạch bài dạy) GDPT 2018 theo CV 5512: mục tiêu, 4 hoạt động, đánh giá. Dùng khi giáo viên cần soạn bài.
---

# Soạn giáo án / kế hoạch bài dạy theo chương trình GDPT 2018

## Khi nào dùng
- Giáo viên cần soạn kế hoạch bài dạy cho một bài/chủ đề cụ thể, kèm phiếu học tập, rubric, bài giảng slide.
- Không dùng cho: ra đề kiểm tra (skill `ra-de-ma-tran`), nhận xét học bạ (`nhan-xet-hoc-ba`), xáo đề (`xao-de-thi`).

## Hỏi lại (chỉ khi thiếu; gom MỘT lần bằng ask_user với `questions`, mỗi câu kèm options)
1. Cấp/lớp và môn (vd THCS - Toán 7). 2. Tên bài hoặc chủ đề, số tiết. 3. Bộ sách (Kết nối tri thức / Chân trời sáng tạo / Cánh diều / khác). 4. Mẫu giáo án của trường (nếu có file, đọc bằng `read_document` và làm theo mẫu đó). 5. Điều kiện lớp: máy chiếu, thiết bị, sĩ số.
Nếu người dùng đã nói đủ thì làm ngay, ghi rõ giả định ở cuối.

## Công cụ
- `read_document`: đọc mẫu giáo án/phân phối chương trình/SGK người dùng gửi.
- `web_search`, `web_fetch`: chỉ để tra yêu cầu cần đạt hoặc ví dụ thực tế; không chép nguyên văn nội dung có bản quyền.
- `create_docx`: xuất giáo án (Markdown: tiêu đề, bảng hoạt động). `create_pptx`: xuất slide bài giảng khi được yêu cầu.
- `docx_fill_template`: khi cần tạo hàng loạt phiếu học tập/giáo án từ một mẫu của trường.
- `plan_set`/`plan_update`: với giáo án nhiều tiết (cập nhật từng bước).

## Quy trình
1. Xác định yêu cầu cần đạt của bài (từ chương trình môn học). Nếu không chắc nội dung, ghi "cần đối chiếu chương trình" thay vì bịa.
2. Viết mục tiêu đo được: động từ quan sát được (nêu, so sánh, giải thích, vận dụng, thiết kế...), không dùng "hiểu", "biết" chung chung.
3. Thiết kế 4 hoạt động; mỗi hoạt động đủ a) Mục tiêu, b) Nội dung, c) Sản phẩm, d) Tổ chức thực hiện (4 bước: giao nhiệm vụ - thực hiện - báo cáo, thảo luận - kết luận, nhận định).
4. Tính thời lượng từng hoạt động, tổng đúng bằng số tiết (1 tiết THCS 45 phút, THPT 45 phút; tiểu học 35 phút).
5. Soạn học liệu: phiếu học tập, câu hỏi, rubric (xem `templates/`).
6. Thêm phân hóa: nhiệm vụ cơ bản + nâng cao + hỗ trợ.
7. Xuất file bằng `create_docx`, rà checklist rồi báo kết quả.

## Mẫu đầu ra (khung theo CV 5512)
Xem `templates/khung-giao-an.md` (khung đầy đủ) và `templates/phieu-hoc-tap.md`. Ví dụ rút gọn hoạt động Mở đầu cho Toán 7 "Tỉ lệ thức":
- a) Mục tiêu: HS nêu được tỉ số hai đại lượng cùng loại từ tình huống pha nước chanh.
- b) Nội dung: so sánh 2 công thức pha (2 chanh:3 đường và 4 chanh:6 đường).
- c) Sản phẩm: nhận xét của HS "hai công thức cho vị giống nhau" và câu hỏi nảy sinh.
- d) Tổ chức: GV chiếu tình huống (giao nhiệm vụ); HS làm cặp 3 phút (thực hiện); 2 cặp trình bày (báo cáo); GV chốt vấn đề bài học (kết luận).

## Quy tắc quyết định
- Môn thực hành/thí nghiệm: tách rõ chuẩn bị, an toàn, thao tác, thu dữ liệu.
- Bài ôn tập: hoạt động luyện tập chiếm ≥ 50% thời lượng.
- Lớp 1-5: câu lệnh ngắn, trò chơi học tập; THPT: nhiệm vụ dự án, tranh luận.
- Thiếu thông tin: đưa phương án mặc định nêu rõ giả định, đừng hỏi dồn dập.

## Checklist tự kiểm
- [ ] Mỗi mục tiêu có động từ đo được và có hoạt động tương ứng.
- [ ] Mỗi hoạt động có đủ a-b-c-d; có sản phẩm kiểm chứng được.
- [ ] Tổng thời lượng bằng số tiết.
- [ ] Có phiếu học tập/rubric và hoạt động phân hóa.
- [ ] Mọi chỗ cần SGK/ngữ liệu bản quyền ghi "xem SGK trang…" để giáo viên điền.
- [ ] File đã tạo bằng `create_docx` (và `create_pptx` nếu được yêu cầu).

## Lỗi thường gặp
Mục tiêu chung chung; hoạt động toàn thầy giảng; thiếu bước kết luận; thời gian không cộng đúng; chép sai yêu cầu cần đạt; nhầm Công văn 5512 (kế hoạch bài dạy) với 2345 (tiểu học, cần kiểm chứng văn bản hiện hành của địa phương).

## Giới hạn
Không bịa nội dung SGK, số liệu, tên tác phẩm hay trích dẫn; không chép nguyên văn nội dung có bản quyền. Đây là bản nháp để giáo viên chỉnh theo lớp của mình. Văn bản hướng dẫn mới của Sở/Phòng GD có thể khác: ghi "cần kiểm chứng".
