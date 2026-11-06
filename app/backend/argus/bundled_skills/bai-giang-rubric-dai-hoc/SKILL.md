---
name: bai-giang-rubric-dai-hoc
description: Soạn đề cương học phần (CLO), bài giảng, rubric chấm bài, đề thi đại học cho giảng viên. Dùng khi cần thiết kế học phần.
---

# Giảng viên đại học: đề cương, bài giảng, rubric

## Khi nào dùng / không dùng
Dùng: đề cương chi tiết học phần (chuẩn đầu ra CLO, phương pháp, đánh giá), bài giảng/slide, rubric chấm bài tập lớn - đồ án - thuyết trình, đề thi và đáp án. Không dùng cho giáo viên phổ thông (dùng `giao-an-gdpt-2018`).

## Hỏi lại (gom một lần bằng ask_user questions)
Tên học phần, số tín chỉ, ngành/chương trình đào tạo; chuẩn đầu ra chương trình (PLO) nếu có; đối tượng (năm mấy, sĩ số); hình thức đánh giá hiện hành (chuyên cần/giữa kỳ/cuối kỳ/đồ án); mẫu đề cương của khoa (đọc bằng `read_document`).

## Công cụ
`read_document` (mẫu đề cương, bài báo, giáo trình), `web_search`/`web_fetch` (tham khảo giáo trình, chuẩn nghề nghiệp — không chép nguyên văn), `create_docx` (đề cương, đề, rubric), `create_pptx` (bài giảng), `create_xlsx` (ma trận CLO-đánh giá, bảng điểm), `grade_summary(path, he_so, output_path)` (tổng hợp điểm quá trình/cuối kỳ), `docx_fill_template` (nhận xét hoặc phiếu điểm hàng loạt), `shuffle_exam` (đề trắc nghiệm nhiều mã), `compare_documents(path_a, path_b)` (so sánh phiên bản đề cương/đề cũ-mới), `convert_to_pdf`.

## Quy trình
1. Xác định CLO viết theo động từ Bloom (nhớ, hiểu, áp dụng, phân tích, đánh giá, sáng tạo), mỗi CLO đo được. 2. Lập ma trận CLO - nội dung - phương pháp - đánh giá (xem `templates/rubric-va-clo.md`). 3. Chia buổi học: mục tiêu, nội dung, hoạt động, bài tập, tài liệu. 4. Soạn rubric theo tiêu chí có trọng số và 4 mức mô tả hành vi quan sát được. 5. Soạn đề/đáp án bám CLO; tổng trọng số = 100%. 6. Xuất file và rà checklist.

## Mẫu đầu ra
Rubric thuyết trình (trọng số): Nội dung 40% (Xuất sắc: lập luận chặt, số liệu chính xác, có phản biện; Tốt; Đạt; Chưa đạt) – Cấu trúc 20% – Trình bày/slide 20% – Trả lời câu hỏi 20%. Mỗi ô mô tả hành vi quan sát được, không dùng từ mơ hồ ("tốt", "kém").

## Quy tắc quyết định
- Mỗi CLO có ít nhất một hình thức đánh giá đo nó.
- Bài nhóm: có phần đánh giá đóng góp cá nhân.
- Quy chế đào tạo (thang điểm 10/4, điều kiện dự thi): theo quy chế của trường — ghi "cần kiểm chứng với quy chế trường".

## Checklist tự kiểm
- [ ] Mỗi CLO có động từ đo được và gắn với đánh giá.
- [ ] Tổng trọng số rubric/điểm thành phần = 100%.
- [ ] Rubric có 4 mức với mô tả quan sát được.
- [ ] Đề/đáp án bám CLO; file đã tạo bằng `create_docx`/`create_xlsx`.

## Lỗi thường gặp
CLO chung chung ("hiểu về…"); đánh giá không đo CLO; rubric chồng chéo tiêu chí; trọng số không cộng 100%; lẫn đề cương cho nhiều khóa.

## Giới hạn
Không bịa tài liệu tham khảo, số liệu hay quy chế; không chép giáo trình có bản quyền. Đề cương là bản nháp để giảng viên và khoa duyệt.
