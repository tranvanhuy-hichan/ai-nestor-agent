---
name: cham-soc-khach-hang
description: "Soạn phản hồi khiếu nại, hỏi đáp khách hàng theo chính sách; phân loại và tổng hợp phản hồi; lập FAQ. Dùng khi xử lý chăm sóc khách hàng."
---

# Chăm sóc khách hàng

## Khi nào dùng / không dùng
- DÙNG: soạn trả lời khiếu nại, hỏi giá, hỏi bảo hành, xin hoàn tiền theo chính sách công ty; phân loại và đếm phản hồi trong file; rút FAQ từ phản hồi lặp lại; kịch bản trả lời mẫu; báo cáo hài lòng khách hàng.
- KHÔNG dùng: hứa hoàn tiền, bồi thường, giảm giá, ngoại lệ chính sách (phải người có thẩm quyền duyệt); tranh chấp pháp lý (phap-che).

## Hỏi lại (gom một lần bằng ask_user questions)
1. Nội dung khách phản hồi (dán/ file) và kênh (email, chat, mạng xã hội, điện thoại).
2. Chính sách áp dụng (đổi trả, bảo hành, giá, thời hạn xử lý) ở file/kho nào.
3. Giọng điệu thương hiệu, tên người ký, thông tin liên hệ.
4. Với tổng hợp: kỳ dữ liệu, cột nào là nội dung/ngày/kênh, nhóm phân loại mong muốn.

## Công cụ
| Việc | Công cụ |
|---|---|
| Tìm chính sách, quy trình, câu trả lời mẫu | kb_search, read_document |
| Soạn phản hồi | create_docx (hoặc trả lời trực tiếp trong chat) |
| Phân loại, đếm phản hồi hàng loạt | run_script (pandas), excel_audit(path) kiểm file đầu vào |
| Bảng tổng hợp có công thức | create_xlsx (COUNTIFS theo nhóm, tháng) |
| Gộp nhiều file phản hồi | excel_merge_reports(paths, output_path, header_hints) |
| FAQ, báo cáo | create_docx, create_pptx |

## Quy trình phản hồi một khách
1. Xác định: loại vấn đề (sản phẩm lỗi, giao chậm, tính phí sai, thái độ nhân viên, câu hỏi thông tin), mức khẩn, cảm xúc (giận/bình thường).
2. Tìm chính sách liên quan bằng kb_search; chỉ dùng điều khoản có thật.
3. Cấu trúc thư: (1) Cảm ơn và ghi nhận; (2) Xin lỗi cụ thể nếu có lỗi từ phía công ty (không xin lỗi chung chung khi chưa rõ); (3) Nêu những gì đã kiểm tra hoặc sẽ kiểm tra, thời hạn; (4) Giải pháp theo chính sách, hoặc 'chúng tôi sẽ chuyển bộ phận … và phản hồi trước …'; (5) Cách liên hệ tiếp.
4. Thiếu căn cứ chính sách hoặc cần ngoại lệ: soạn bản 'xin ý kiến quản lý' kèm tóm tắt vụ việc; thư gửi khách nói rõ sẽ chuyển người phụ trách, KHÔNG hứa.
5. Giữ đúng dữ kiện khách cung cấp (mã đơn, ngày, số tiền); thiếu thì hỏi ngắn trong thư.

## Quy trình tổng hợp
1. excel_audit/read kiểm file; xác định cột. 2. Phân loại theo bộ nhóm thống nhất (do người dùng chọn hoặc đề xuất 6-10 nhóm), có nhóm 'khác'. 3. Đếm bằng công thức COUNTIFS; theo tháng/kênh/nhóm. 4. Trích 3-5 phản hồi tiêu biểu mỗi nhóm lớn (nguyên văn, ẩn thông tin cá nhân). 5. Gợi ý cải tiến dựa trên số liệu. 6. FAQ: nhóm câu hỏi lặp từ 3 lần trở lên, mỗi mục có câu trả lời bám chính sách.

## Mẫu đầu ra
Thư: 'Kính gửi Anh/Chị ……, Cảm ơn Anh/Chị đã phản hồi về đơn hàng …… . Chúng tôi rất tiếc về việc ……. Chúng tôi đã ghi nhận và sẽ kiểm tra với bộ phận ……; dự kiến phản hồi chi tiết trước ……. Nếu cần hỗ trợ gấp, Anh/Chị vui lòng liên hệ ……. Trân trọng, ……'.
Bảng tổng hợp: Nhóm | Số phản hồi (=COUNTIFS) | % | Ví dụ tiêu biểu | Đề xuất.

## Quy tắc quyết định
- Khách yêu cầu hoàn tiền/bồi thường: chỉ nêu điều kiện theo chính sách; quyết định do người có thẩm quyền.
- Khách có nội dung đe dọa, tố cáo pháp lý, báo chí: không tranh luận; soạn bản chuyển quản lý, nhắc phap-che.
- Thông tin cá nhân của khách (số điện thoại, địa chỉ): không đưa vào FAQ/báo cáo chung.
- Chính sách mâu thuẫn nhau: nêu cả hai, hỏi bản hiện hành.

## Checklist tự kiểm
- [ ] Câu trả lời bám chính sách có trong kho hoặc đánh dấu 'cần xác nhận'.
- [ ] Không có cam kết hoàn tiền, bồi thường, thời hạn nào chưa được duyệt.
- [ ] Thông tin vụ việc (mã đơn, ngày, số tiền) đúng như khách cung cấp.
- [ ] Bảng tổng hợp đếm bằng công thức; tổng các nhóm = tổng số phản hồi.
- [ ] Thư là bản nháp chưa gửi; thông tin cá nhân khách được ẩn trong báo cáo chung.

## Lỗi thường gặp
- Xin lỗi chung chung hoặc đổ lỗi cho khách.
- Hứa thời hạn xử lý không có thật.
- Tổng hợp đếm sai do trùng hoặc phân loại chồng chéo.

## Giới hạn
- Không gửi thư, không hoàn tiền, không thay đổi đơn hàng/tài khoản khách.
- Không bịa chính sách, thời hạn, thông tin đơn hàng. Dữ liệu khách chỉ xử lý trong thư mục làm việc.
