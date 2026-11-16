---
name: dau-tu-cong
description: "Hồ sơ đầu tư công cấp xã/phường: soạn báo cáo đề xuất chủ trương, tờ trình thẩm định; kiểm tra dự toán; trích căn cứ, dữ liệu dự án."
---

# Đầu tư công cấp xã/phường

## Khi nào dùng / không dùng
- DÙNG: hồ sơ dự án do UBND xã/phường làm chủ đầu tư hoặc thẩm định: báo cáo đề xuất chủ trương đầu tư (kể cả dự án nhóm C), tờ trình, thông báo kết quả thẩm định, quyết định phê duyệt; kiểm tra dự toán/báo cáo kinh tế - kỹ thuật; trích xuất thông tin dự án, căn cứ pháp lý, tiêu chuẩn kỹ thuật từ hồ sơ.
- KHÔNG dùng: văn bản hành chính chung (van-thu-nd30), đối chiếu sổ kế toán (ke-toan), đấu thầu doanh nghiệp (mua-sam-dau-thau).
- Quy định đầu tư công thay đổi thường xuyên: chỉ nêu điều luật khi lấy từ tài liệu của người dùng (kho kb_search) hoặc chắc chắn; còn lại ghi 'cần kiểm chứng'.

## Hỏi lại (gom một lần bằng ask_user questions)
1. TÌNH HUỐNG: dự án đầu tư công MỚI (có trong kế hoạch vốn, theo luật đầu tư công) hay sửa chữa/mua sắm/thuê dịch vụ từ chi thường xuyên? Hai trường hợp thẩm quyền, quy trình khác nhau.
2. Tên dự án, chủ đầu tư, địa điểm, nguồn vốn, tổng mức dự kiến, nhóm dự án, giai đoạn hồ sơ (chủ trương / lập BCKTKT / thẩm định / phê duyệt).
3. Thư mục hồ sơ (quyết định, tờ trình, dự toán, bản vẽ, thuyết minh, báo cáo thẩm tra) và kho tài liệu pháp lý của địa phương.
4. Việc cần làm: soạn văn bản nào, kiểm tra điều gì, trích xuất trường nào.

## Công cụ
| Việc | Công cụ |
|---|---|
| Tìm căn cứ, quy trình, phân cấp trong kho của người dùng | kb_search |
| Đọc hồ sơ Word/PDF, bản scan | read_document, view_image |
| Kiểm tra dự toán Excel: số học, công thức, tổng | excel_audit(path) |
| Kiểm tra tính lại phức tạp, đối chiếu giá với bảng giá người dùng | run_script |
| Gộp nhiều bảng dự toán/biểu mẫu | excel_merge_reports(paths, output_path, header_hints) |
| So hai phiên bản hồ sơ/dự toán | compare_documents(path_a, path_b) |
| Dựng văn bản đúng NĐ 30 | vanban_types, vanban_write_docx (TO_TRINH, BAO_CAO, BAO_CAO_CO_BANG, QUYET_DINH_...), review_vn_document |
| Bảng trích xuất, checklist | create_xlsx |
| Hồ sơ lớn nhiều phần | team_run (đọc hồ sơ, kiểm dự toán, soạn, rà), plan_set |
| Xuất PDF | convert_to_pdf(path) |

## Quy trình
1. Phân loại tình huống A (dự án đầu tư công mới) hay B (chi thường xuyên); hỏi nếu chưa rõ. Nêu kết quả phân loại cho người dùng.
2. kb_search tìm căn cứ liên quan (luật, nghị định, quyết định phân cấp, quy trình địa phương). Chỉ trích điều khoản ĐÃ ĐỌC từ nguồn.
3. Đọc hồ sơ; trích xuất dữ liệu vào bảng có chứng cứ: Trường | Giá trị | File nguồn | Trang/bảng | Độ chắc chắn.
4. Căn cứ pháp lý của MỘT văn bản chỉ lấy từ khối 'Căn cứ' của chính văn bản đó; chỉ lấy văn bản gốc, bỏ phần 'đã được sửa đổi, bổ sung theo ...'; tiêu chuẩn TCVN/QCVN chỉ khi văn bản thật sự dẫn chiếu và giữ nguyên số phần (ví dụ TCVN 7572-20:2006). Mỗi văn bản xử lý ĐỘC LẬP; tờ trình hành chính thường không có tiêu chuẩn (để rỗng).
5. Kiểm dự toán: excel_audit để quét công thức/số học; dựng checklist theo cấu trúc chi phí: xây dựng, thiết bị, quản lý dự án, tư vấn, chi phí khác, dự phòng; tính lại thành tiền = khối lượng × đơn giá, tổng nhóm, thuế, tỷ lệ. Đơn giá, định mức CHỈ lấy từ bảng giá/kho của người dùng; không có thì ghi 'không có trong kho', không tự điền.
6. Soạn văn bản: vanban_types rồi vanban_write_docx; chỗ thiếu '……'; review_vn_document.
7. Hồ sơ lớn: team_run chia vai, nhưng kiểm tra dự toán nên làm trong một phiên để tránh lệch kết quả.
8. Báo: văn bản đã tạo, bảng trích xuất, checklist dự toán, danh sách điểm người có thẩm quyền cần xác nhận.

## Mẫu đầu ra
- Bảng trích xuất: Trường | Giá trị | File nguồn | Trang/bảng | Độ chắc chắn.
- Checklist dự toán: Hạng mục | Vị trí (sheet/dòng) | Số trong hồ sơ | Số tính lại | Chênh lệch | Nguồn đối chiếu | Mức ảnh hưởng. Xếp theo mức ảnh hưởng tiền giảm dần; lỗi làm sai tổng mức đứng trước. Chênh lệch làm tròn dưới khoảng 1% không báo là lỗi.
- Báo cáo đề xuất chủ trương: Sự cần thiết; Mục tiêu; Quy mô, địa điểm, thời gian; Tổng mức, nguồn vốn, phân kỳ; Hiệu quả; Tổ chức thực hiện; Kiến nghị (khung nội dung, đối chiếu mẫu hiện hành khi dựng).

## Quy tắc quyết định
- Thẩm quyền quyết định chủ trương/phê duyệt phụ thuộc phân cấp của địa phương và loại dự án: lấy từ quyết định phân cấp trong kho của người dùng; không có thì 'cần kiểm chứng', không nêu cấp.
- Chênh lệch giá vs bảng giá: chỉ kết luận khi cùng quy cách, cùng đơn vị, cùng cơ sở (đã/chưa VAT); khác cơ sở thì ghi lý do và không kết luận sai.
- Không chắc là lỗi thì KHÔNG đưa vào danh sách lỗi; chuyển sang 'cần xác nhận'.

## Checklist tự kiểm
- [ ] Đã phân loại A/B và nêu cho người dùng.
- [ ] Mỗi dữ liệu quan trọng có chứng cứ (file, trang/bảng).
- [ ] Không đơn giá, định mức, điều khoản nào do nhớ rồi tự điền; thiếu thì 'cần kiểm chứng'.
- [ ] Đã chạy excel_audit hoặc run_script tính lại tổng và các thành phần.
- [ ] Văn bản dựng bằng vanban_write_docx; review_vn_document không còn [LỖI].
- [ ] Danh sách điểm cần xác nhận đã báo.

## Lỗi thường gặp
- Trộn thẩm quyền của dự án đầu tư công mới với chi thường xuyên.
- Đưa văn bản sửa đổi vào danh sách căn cứ độc lập; rút gọn số hiệu TCVN nhiều phần.
- Dùng chung một danh sách tiêu chuẩn cho nhiều văn bản.
- Báo lỗi do làm tròn; dùng giá cũ hoặc không rõ nguồn.

## Giới hạn
- Không tự phê duyệt, thẩm định thay cơ quan có thẩm quyền; không nộp hồ sơ lên hệ thống.
- Không bịa số văn bản, đơn giá, định mức, điều luật.
- Không đưa hồ sơ ra dịch vụ bên ngoài khi chưa được phép.
