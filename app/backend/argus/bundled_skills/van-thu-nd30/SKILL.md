---
name: van-thu-nd30
description: "Soạn công văn, tờ trình, báo cáo, quyết định, thông báo, kế hoạch, giấy mời đúng NĐ 30/2020. Dùng khi tạo mới hoặc dựng lại văn bản hành chính nhà nước thành file Word."
---

# Soạn văn bản hành chính đúng NĐ 30/2020/NĐ-CP

## Khi nào dùng / không dùng
- DÙNG khi người dùng nhờ soạn MỘT văn bản hành chính của cơ quan nhà nước: công văn, tờ trình, báo cáo, quyết định, kế hoạch, thông báo, giấy mời, biên bản, công điện, giấy giới thiệu, giấy nghỉ phép.
- DÙNG khi có bản nháp thô (ghi chú, văn bản cũ, ảnh chụp) cần dựng lại đúng thể thức.
- KHÔNG dùng cho văn bản của Đảng (xem skill van-ban-dang-hd05), báo cáo/bài viết học thuật, thư từ của doanh nghiệp (dùng create_docx), hợp đồng thương mại.
- Chỉ muốn kiểm tra file có sẵn: dùng skill ra-soat-the-thuc, không soạn lại.

## Hỏi lại (gom MỘT lần bằng ask_user với tham số questions, chỉ hỏi cái còn thiếu)
1. Loại văn bản (nếu người dùng chưa nói và không suy ra được).
2. Cơ quan chủ quản và cơ quan ban hành, theo tên hiện hành (cấp xã/phường: mô hình hai cấp từ 01/7/2025; nếu nghi ngờ hãy hỏi tên đơn vị chính xác).
3. Nơi nhận (Kính gửi), nội dung/trích yếu, căn cứ pháp lý cần dẫn, số liệu đi kèm.
4. Người ký, chức danh, ký trực tiếp hay TM./KT./TL./TUQ.; địa danh và ngày ban hành; số và ký hiệu (chưa có thì để ……).
5. Có file mẫu hoặc văn bản cũ của cơ quan không (đọc bằng read_document).
Câu nào người dùng đã nêu thì KHÔNG hỏi lại. Số/ký hiệu, ngày ban hành, người ký chưa biết thì để '……' và đi tiếp; KHÔNG hỏi thêm về nội dung, tự viết (xem mục 'Viết nội dung đầy đủ').

## Viết nội dung đầy đủ (bắt buộc, không giao khung rỗng)
Người dùng chỉ đưa một câu như 'soạn tờ trình đề nghị xây dựng quốc lộ 14E' vẫn phải nhận được văn bản hoàn chỉnh, đọc là dùng được. Bạn tự suy luận và tự viết toàn bộ phần lập luận.
1. TRA CỨU TRƯỚC KHI VIẾT (có web_search/web_fetch): tìm 2-3 văn bản thật cùng loại và cùng lĩnh vực (VD 'tờ trình đề nghị chủ trương đầu tư dự án đường giao thông', 'căn cứ Luật Đầu tư công 2024', 'quy hoạch mạng lưới đường bộ') để lấy bố cục, cách lập luận, và căn cứ pháp lý đang có hiệu lực. Mở trang chứa văn bản bằng web_fetch khi cần đọc kỹ. Chỉ dẫn căn cứ bạn đã thấy tận mắt kèm số hiệu và ngày ban hành; không chắc thì ghi 'cần kiểm chứng'.
2. Bộ khung nội dung theo loại (viết thành câu, đoạn đầy đủ, không để tiêu đề trơ):
   - Tờ trình: (1) Sự cần thiết/căn cứ pháp lý và thực tiễn; (2) Mục tiêu, phạm vi, quy mô, địa điểm, hình thức đầu tư/giải pháp; (3) Sơ bộ tổng mức, nguồn lực, tiến độ (số ước tính ghi '(dự kiến, cần xác nhận)'); (4) Hiệu quả và rủi ro; (5) Kiến nghị cụ thể mong cấp trên quyết định, kèm hồ sơ đính kèm.
   - Công văn: căn cứ/lý do, nội dung đề nghị hoặc trả lời có hạn và đầu mối, trách nhiệm thực hiện.
   - Báo cáo: tình hình và số liệu, kết quả, tồn tại và nguyên nhân, phương hướng, kiến nghị. Quyết định: căn cứ, điều khoản nội dung, hiệu lực, trách nhiệm thi hành. Kế hoạch: mục đích yêu cầu, nội dung, phân công, thời gian, kinh phí. Thông báo/giấy mời: thời gian, địa điểm, thành phần, nội dung, chuẩn bị.
3. Số liệu cụ thể chưa được cung cấp (chiều dài tuyến, tổng mức đầu tư...): nếu tra cứu hoặc suy ra được thì điền số tham khảo kèm '(dự kiến, cần xác nhận)'; nếu hoàn toàn không có cơ sở thì viết câu định tính ('khoảng … km') chứ không bỏ cả đoạn.
4. Chỉ '……' ở: số/ký hiệu, ngày ban hành, họ tên người ký (và địa danh nếu thật sự không biết). Không lấy tên người dùng làm người ký nếu họ chưa nói.
5. Độ dài: tờ trình/báo cáo thường 2-4 trang nội dung; công văn 1-2 trang. Bản chỉ có tiêu đề và vài dấu '……' là chưa đạt.

## Công cụ
| Việc | Công cụ |
|---|---|
| Xem loại văn bản, cấu trúc role bắt buộc, quy tắc dựng | vanban_types (không tham số = danh sách; document_type_key = chi tiết) |
| Ghi file .docx đúng thể thức | vanban_write_docx(path, document_type_key, paragraphs) — luôn dùng, KHÔNG dùng create_docx |
| Rà thể thức sau khi ghi | review_vn_document(path) |
| Đọc mẫu/văn bản cũ/ảnh scan | read_document, view_image |
| So bản cũ - bản mới khi sửa văn bản | compare_documents(path_a, path_b) |
| Xuất PDF khi người dùng cần | convert_to_pdf(path) |
| Văn bản dài, nhiều phần | plan_set rồi làm lần lượt |
| Tìm căn cứ trong kho tài liệu của người dùng | kb_search |
| Tìm văn bản mẫu và căn cứ pháp lý trên internet | web_search, web_fetch |

## Quy trình từng bước
1. vanban_types để chọn document_type_key; rồi vanban_types(document_type_key=...) lấy structure. Không tự bịa key hay role.
2. Có mẫu/văn bản cũ: read_document để lấy cấu trúc mục, văn phong, nội dung cố định (tên cơ quan in sẵn, câu khung) và chép NGUYÊN VĂN phần cố định; bỏ qua mọi thông tin định dạng của mẫu (font, cỡ, canh lề chỉ do writer quyết định).
3. Lập dàn ý đúng thứ tự structure. Mẫu có thể có thêm mục phụ nhưng không được thiếu role bắt buộc; role bắt buộc chưa có nội dung vẫn tạo với '……'.
4. Tra cứu mẫu và căn cứ (web_search/web_fetch), rồi viết ĐẦY ĐỦ nội dung theo mục 'Viết nội dung đầy đủ'. Chỉ số văn bản, ngày ký, người ký để '……'; số tiền ước tính ghi '(dự kiến, cần xác nhận)'; căn cứ pháp lý chỉ dẫn văn bản có thật đã tra.
5. Dựng paragraphs theo mẫu trong templates/ (xem bên dưới) rồi thay nội dung. Mỗi dòng trong left_lines/right_lines là OBJECT {"role","text"}, không phải chuỗi.
6. vanban_write_docx đúng một lần. Có CẢNH BÁO thiếu role hoặc lỗi cấu trúc thì sửa đúng chỗ, gọi lại tối đa một lần.
7. review_vn_document; còn [LỖI] thì sửa nội dung và tạo lại (không sửa tay file).
8. Báo người dùng: đường dẫn file, các chỗ '……' cần điền, điểm cần kiểm chứng (căn cứ pháp lý, số liệu), việc họ cần quyết định (ký thay, số hiệu).

## BỐ CỤC ĐẦU VÀ CUỐI VĂN BẢN (bắt buộc dùng two_columns)
- Đầu văn bản là MỘT khối layout two_columns: BÊN TRÁI = cơ quan chủ quản (parent_org), cơ quan ban hành (issuing_org), số ký hiệu (document_number) [công văn thêm trích yếu summary_cong_van]; BÊN PHẢI = quốc hiệu (national_name), tiêu ngữ (motto), địa danh - ngày tháng (place_date). KHÔNG xếp các dòng này thành các đoạn dọc ở giữa trang.
- Cuối văn bản là MỘT khối two_columns: BÊN TRÁI = Nơi nhận, BÊN PHẢI = quyền hạn ký, chức vụ, họ tên.
- Cứ sao chép khối đầu và khối cuối từ templates/, chỉ đổi chữ. Công cụ vanban_write_docx tự ghép lại nếu bạn lỡ để rời, nhưng đừng dựa vào đó.

## Mẫu đầu ra
Thư mục templates/ có sẵn paragraphs JSON hợp lệ (đã kiểm tra bằng writer) để sao chép và thay chữ:
- templates/cong-van.paragraphs.json (CONG_VAN)
- templates/to-trinh.paragraphs.json (TO_TRINH)
- templates/bao-cao.paragraphs.json (BAO_CAO)
- templates/thong-bao.paragraphs.json (THONG_BAO)
- templates/quyet-dinh.paragraphs.json (QUYET_DINH_TRUC_TIEP)
- templates/giay-moi.paragraphs.json (GIAY_MOI)
Đọc file mẫu bằng skills_read hoặc read, đổi giá trị text, rồi truyền chuỗi JSON vào tham số paragraphs.

Ví dụ nhập - xuất: "Soạn công văn đôn đốc các phòng nộp báo cáo quý III, hạn 15/10, UBND phường Hải Châu, ký chủ tịch" → hỏi gộp (số hiệu? ngày ban hành? danh sách phòng?) → CONG_VAN với summary_cong_van 'V/v đôn đốc nộp báo cáo quý III năm 2026', recipient 'Kính gửi: Các phòng, ban thuộc UBND phường', body 3 đoạn (căn cứ, đề nghị cụ thể có hạn 15/10, trách nhiệm), nơi nhận + chữ ký cạnh nhau; số văn bản '……/UBND-……' nếu chưa cấp.

## Quy tắc quyết định
- Tờ trình hay báo cáo? Gửi xin quyết định/phê duyệt = TỜ TRÌNH; thông tin kết quả/tình hình = BÁO CÁO. Không rõ thì hỏi.
- Quyết định ban hành kèm văn bản khác (quy chế, kế hoạch) = QUYET_DINH_GIAN_TIEP; quy định trực tiếp các điều = QUYET_DINH_TRUC_TIEP.
- Báo cáo có bảng số liệu: dùng BAO_CAO_CO_BANG hoặc item layout table (đúng MỘT item cho mỗi bảng, mọi dòng trong table_rows).
- Công văn: không có document_type_title, dùng summary_cong_van; thông báo: không có legal_basis.
- Người ký không phải người đứng đầu: thêm TM./KT./TL./TUQ. vào signature_authority, CHỈ khi người dùng xác nhận.
- Bảng từ khoảng 6 cột: section_orientation landscape trên item đó, rồi đặt lại portrait; phụ lục bắt đầu trang mới (page_break_before true), trừ item đổi hướng giấy.
- Kính gửi từ 2 cơ quan: mỗi cơ quan một item recipient (không dùng \n), các dòng trước dòng cuối đặt no_underline true.

## Checklist tự kiểm (đều phải kiểm chứng được)
- [ ] File tạo bằng vanban_write_docx; review_vn_document không còn [LỖI].
- [ ] Mỗi role một dòng một text; tên cơ quan không bị tự tách dòng; quốc hiệu nằm trọn một dòng.
- [ ] Nơi nhận và chữ ký nằm cạnh nhau (two_columns), kể cả một người ký.
- [ ] Mục La Mã là section_heading (đậm); từng văn bản pháp luật dẫn chiếu là legal_basis.
- [ ] Phần nội dung chính đã viết đầy đủ (không chỉ khung); '……' chỉ ở số/ký hiệu, ngày ký, người ký.
- [ ] Mọi văn bản pháp luật dẫn chiếu là có thật (đã tra), đúng số hiệu; số ước tính ghi '(dự kiến, cần xác nhận)'; không bịa tên người.
- [ ] Địa danh/cấp hành chính theo mô hình hai cấp; không còn tên huyện/quận cũ ngoài ý muốn.
- [ ] Đã liệt kê cho người dùng các chỗ '……' và điểm cần kiểm chứng.

## Lỗi thường gặp
- left_lines/right_lines là danh sách chuỗi thay vì object {role, text} (writer sẽ từ chối với thông báo rõ).
- 'I. Các căn cứ...' bị gán legal_basis (nghiêng) thay vì section_heading (đậm).
- Nhét 'Công trình: ... Địa điểm: ...' vào một summary dài; đúng là nhiều item summary, mọi dòng trừ dòng cuối no_underline true.
- Tách một bảng thành nhiều item table; để Nơi nhận và chữ ký thành hai khối xếp dọc.
- Dùng create_docx cho văn bản hành chính (sai thể thức; hệ thống sẽ chặn).
- Tự render ảnh/PDF để soi: không cần, kết quả applied và review_vn_document là căn cứ.

## Giới hạn
- Chỉ tạo bản dự thảo; không ký, đóng dấu, gửi, ban hành hay nộp thay người dùng.
- Không bịa số hiệu, ngày, tên người, số tiền, trích dẫn điều luật. Chỉ nêu căn cứ pháp lý khi chắc chắn hoặc lấy từ tài liệu người dùng; còn lại ghi 'cần kiểm chứng'.
- Không đổi thẩm quyền ký (TM./KT./TL./TUQ.) khi chưa được xác nhận.
