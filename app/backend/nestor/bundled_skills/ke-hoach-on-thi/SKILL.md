---
name: ke-hoach-on-thi
description: Lập kế hoạch ôn thi theo số ngày còn lại, ra đề luyện, chấm và chỉ ra lỗ hổng kiến thức. Dùng khi học sinh chuẩn bị kỳ thi.
---

# Ôn thi và luyện đề

## Khi nào dùng / không dùng
Dùng: lộ trình ôn tập, bảng theo dõi tiến độ, đề luyện và chấm bài. Không dùng để giải đề thi đang diễn ra hay đoán đề thi thật.

## Hỏi lại (gom bằng ask_user questions)
Kỳ thi (giữa kỳ/cuối kỳ/vào lớp 10/tốt nghiệp THPT), ngày thi, các môn và điểm mục tiêu, thời gian rảnh mỗi ngày, môn/chương em yếu, tài liệu em có.

## Công cụ
`create_xlsx` (lịch ôn + bảng theo dõi có công thức % hoàn thành), `create_docx` (đề luyện, đáp án, bảng lỗi sai), `run_script` (tính số buổi, phân bổ thời gian, thống kê điểm luyện), `read_document` (đề cương, đề cũ), `view_image` (ảnh bài làm), `web_search`/`web_fetch` (cấu trúc đề thi chính thức; nêu nguồn), `notify` (nhắc lịch nếu người dùng yêu cầu), `remember` (chỗ yếu).

## Quy trình
1. Tính số ngày còn lại → số buổi thực tế (trừ ngày nghỉ). 2. Ưu tiên: chủ đề điểm cao/em yếu/xuất hiện nhiều → xếp trước; chia 3 giai đoạn: củng cố nền (≈50%), luyện dạng bài (≈30%), luyện đề + tổng ôn (≈20%). 3. Xuất lịch theo ngày: môn - nội dung - thời lượng - mục tiêu (xem `templates/lich-on-tap.md`), cộng thời gian nghỉ (giải lao, ngủ đủ). 4. Ra đề luyện theo cấu trúc đề thi thật (nêu rõ nguồn cấu trúc), thời gian đúng. 5. Chấm: ghi lỗi sai theo nhóm (kiến thức / kỹ năng / cẩu thả / thời gian) và bảng lỗi. 6. Điều chỉnh kế hoạch sau mỗi tuần theo kết quả.

## Mẫu đầu ra
"Còn 45 ngày thi vào lớp 10 (Toán - Văn - Anh), 2,5 giờ/ngày, yếu hình học. Giai đoạn 1 (ngày 1-22): Toán 1h (ưu tiên hình học), Văn 0,75h, Anh 0,75h. Giai đoạn 2 (23-37): luyện dạng bài. Giai đoạn 3 (38-45): mỗi 2 ngày 1 đề đủ thời gian, chữa kỹ." Kèm bảng Excel theo dõi.

## Quy tắc quyết định
- Quỹ thời gian quá ít: nói thật, chọn trọng tâm thay vì nhồi nhét.
- Không khuyên thức khuya liên tục; chèn nghỉ và vận động.
- Cấu trúc/quy chế thi: lấy từ thông báo chính thức; không chắc ghi "cần kiểm chứng".

## Checklist tự kiểm
- [ ] Tổng thời lượng mỗi ngày khớp quỹ thời gian em có.
- [ ] Chủ đề ưu tiên phản ánh điểm yếu của em.
- [ ] Có lịch (xlsx) và đề luyện có đáp án, thang điểm.
- [ ] Có bảng lỗi sai và cách khắc phục.

## Lỗi thường gặp
Lịch quá dày không thực hiện được; ôn dàn trải; luyện đề quá sớm hoặc quá muộn; không rút kinh nghiệm từ lỗi sai; bỏ qua nghỉ ngơi.

## Giới hạn
Không đoán đề thi thật, không hứa điểm số; không làm hộ bài thi; không chép đề thi có bản quyền; sức khỏe tinh thần: nếu em căng thẳng kéo dài, khuyên nói chuyện với thầy cô, gia đình.
