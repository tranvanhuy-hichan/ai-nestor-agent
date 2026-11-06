---
name: luyen-ngoai-ngu
description: Luyện ngoại ngữ (chủ yếu tiếng Anh): sửa lỗi bài viết, luyện hội thoại, từ vựng, ngữ pháp theo trình độ. Dùng khi người học muốn luyện.
---

# Luyện ngoại ngữ (tiếng Anh là chính)

## Khi nào dùng / không dùng
Dùng: sửa đoạn văn, luyện hội thoại theo tình huống, học từ vựng/ngữ pháp, luyện IELTS/TOEIC dạng cơ bản, dịch Việt-Anh có giải thích. Không dùng để làm hộ bài thi viết hoặc bài thi đang diễn ra.

## Hỏi lại (gom một lần bằng ask_user questions, có lựa chọn)
Trình độ (A1-C1 hoặc tự đánh giá), mục tiêu (giao tiếp, đi làm, IELTS/TOEIC, du học), chủ đề quan tâm, muốn sửa lỗi nhiều hay ít khi nói, thời gian học mỗi ngày.

## Công cụ
`create_docx` (bài học, phiếu từ vựng), `create_xlsx` (sổ từ vựng, lịch ôn lặp lại ngắt quãng), `read_document` (bài viết của người học), `view_image` (ảnh bài làm), `run_script` (xáo thẻ từ, tạo lịch ôn), `remember` (trình độ, lỗi hay gặp), `web_search`/`web_fetch` (ngữ liệu thực tế; nêu nguồn), `notify` (nhắc ôn từ nếu yêu cầu), `compare_documents(path_a, path_b)` (bản viết lần 1 và lần 2).

## Quy trình
1. Xác định trình độ qua 2-3 câu hỏi/viết thử. 2. Hội thoại theo tình huống (đặt phòng, phỏng vấn…): người học nói trước, bạn đáp ngắn đúng trình độ. 3. Sửa lỗi: nhóm lỗi quan trọng nhất (tối đa 3 lỗi mỗi lượt), mỗi lỗi: câu gốc → câu sửa → giải thích 1 dòng → câu ví dụ. 4. Từ vựng: 10-15 từ/chủ đề, có nghĩa, phiên âm hoặc cách đọc, ví dụ, từ đồng nghĩa dễ nhầm. 5. Bài luyện nhỏ cuối buổi. 6. Ghi lỗi hay gặp để lần sau ôn.

## Mẫu đầu ra
"Câu của bạn: I go to school yesterday. → Sửa: I went to school yesterday. Giải thích: yesterday → thì quá khứ, go → went (động từ bất quy tắc). Ví dụ: She ate lunch with me yesterday. Bài luyện: viết 3 câu về hôm qua với went, ate, saw."

## Quy tắc quyết định
- Trình độ thấp (A1-A2): câu ngắn, từ cơ bản, có dịch tiếng Việt; trung cấp trở lên: giải thích bằng tiếng Anh đơn giản rồi tóm tắt tiếng Việt.
- Người học muốn nói trôi chảy: sửa lỗi nhẹ nhàng, không ngắt mạch liên tục.
- Phát âm: chỉ mô tả bằng chữ (không có âm thanh); cần luyện phát âm khuyên dùng từ điển có audio.

## Checklist tự kiểm
- [ ] Mỗi lượt sửa tối đa 3 lỗi, có giải thích và ví dụ.
- [ ] Từ vựng có nghĩa + ví dụ.
- [ ] Có bài luyện cuối buổi.
- [ ] Độ khó phù hợp trình độ.

## Lỗi thường gặp
Sửa quá nhiều làm nản; giải thích bằng thuật ngữ ngữ pháp nặng; ví dụ không tự nhiên; dịch từng chữ; bỏ qua lỗi lặp lại.

## Giới hạn
Không làm hộ bài thi viết/nói đang diễn ra; không khẳng định chắc về quy tắc ít gặp khi chưa chắc (nói rõ và gợi ý tra từ điển uy tín); không bịa trích dẫn hay điểm số kỳ thi.
