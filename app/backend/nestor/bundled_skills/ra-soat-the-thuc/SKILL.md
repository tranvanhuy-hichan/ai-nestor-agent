---
name: ra-soat-the-thuc
description: "Rà văn bản .docx trước khi trình ký: thể thức NĐ 30, quốc hiệu, số ký hiệu, nơi nhận, chữ ký, chính tả, số liệu. Dùng khi đã có file cần kiểm tra."
---

# Rà soát văn bản trước khi trình ký

## Khi nào dùng / không dùng
- DÙNG: người dùng đưa MỘT hoặc NHIỀU file .docx (dự thảo) và muốn biết còn lỗi gì trước khi trình ký; so bản sửa với bản trước; kiểm tra sau khi chuyên viên chỉnh.
- KHÔNG dùng: soạn mới (van-thu-nd30), văn bản Đảng (HD 05; review_vn_document chỉ kiểm theo NĐ 30), file PDF/ảnh không có bản Word (đọc được nhưng chỉ rà nội dung, báo rõ không rà được định dạng).

## Hỏi lại (rất ít; gom một lần)
- File nào, và đây là loại văn bản gì (nếu không đoán được từ nội dung).
- Mức rà: chỉ thể thức hay cả nội dung (chính tả, số liệu, căn cứ pháp lý, mâu thuẫn trong văn bản).
- Có được tạo bản đã sửa không (mặc định KHÔNG ghi đè; nếu sửa thì lưu tên khác).

## Công cụ
| Việc | Công cụ |
|---|---|
| Rà thể thức NĐ 30 tự động | review_vn_document(path) (quốc hiệu, tiêu ngữ, số ký hiệu, địa danh ngày, trích yếu, nơi nhận, thẩm quyền ký, font, cấp hành chính cũ) |
| Đọc toàn văn để rà nội dung, chính tả, số liệu | read_document, view_image (ảnh) |
| So bản trước và sau chỉnh sửa | compare_documents(path_a, path_b) |
| Biết loại văn bản cần những khối nào | vanban_types(document_type_key) |
| Tạo bản đã sửa đúng thể thức (nếu được yêu cầu) | vanban_write_docx với tên file khác |
| Xuất PDF để trình | convert_to_pdf(path) |

## Quy trình
1. review_vn_document trên từng file; trích kết quả nguyên văn.
2. read_document để đọc toàn văn. Với loại văn bản đã biết, vanban_types để đối chiếu các khối bắt buộc có đủ không.
3. Rà nội dung theo các nhóm lỗi (xem bảng dưới): chính tả, số liệu cộng trừ, ngày tháng hợp lý, số hiệu/ngày dẫn chiếu có nhất quán trong văn bản, địa danh/cấp hành chính, tên cơ quan nhất quán.
4. Có bản trước: compare_documents để biết phần thay đổi, chỉ rà kỹ phần đó nhưng vẫn quét toàn bộ.
5. Lập báo cáo rà soát: mỗi lỗi có Vị trí (đoạn/mục) | Lỗi | Đề xuất sửa | Mức độ.
6. Chỉ khi được đề nghị: tạo bản đã sửa bằng tên khác (ví dụ ten-file-da-ra-soat.docx), không ghi đè file gốc.

## Phân loại lỗi (mức độ)
| Mức | Ví dụ |
|---|---|
| Bắt buộc sửa | Thiếu quốc hiệu/tiêu ngữ, thiếu số ký hiệu, thiếu nơi nhận, sai thẩm quyền ký (TM./KT./TL./TUQ. không phù hợp), tổng cộng sai |
| Nên sửa | Lỗi chính tả, câu mơ hồ, trích yếu không sát nội dung, địa danh cũ |
| Cần người có thẩm quyền xác nhận | Căn cứ pháp lý có còn hiệu lực không, thẩm quyền ban hành, số liệu không có nguồn |
Ví dụ: 'Số: …/QĐ' thiếu ký hiệu đơn vị = Bắt buộc; 'Huyện Hòa Vang' trong văn bản năm 2026 = Cần xác nhận (cấp hành chính thay đổi); tổng 12 + 8 ghi 21 = Bắt buộc.

## Quy tắc quyết định
- Không chắc là lỗi thì phân vào 'cần xác nhận', không khẳng định sai.
- review_vn_document cho [LỖI] nhưng bạn thấy đúng thực tế (ví dụ chức danh ký ghi ở dạng khác): nêu cả hai, để người dùng quyết.
- Nhiều file: trình bày bảng tóm tắt (file | số lỗi bắt buộc | nên sửa | cần xác nhận) rồi mới đến chi tiết.
- Chỉ rà được nội dung (PDF/ảnh): nói thẳng không rà được định dạng.

## Mẫu báo cáo rà soát
"Đã rà công văn 1 trang. Kết quả: 1 lỗi nghiêm trọng, 2 lỗi cần sửa, 1 gợi ý.
| # | Vị trí | Lỗi | Mức | Đề xuất |
|---|--------|-----|-----|---------|
| 1 | Đầu trang, dòng 3 | Thiếu tiêu ngữ "Độc lập - Tự do - Hạnh phúc" | Nghiêm trọng | Thêm dưới quốc hiệu, in thường, gạch chân |
| 2 | Số ký hiệu | Viết "Số: 12/CV" thiếu chữ viết tắt cơ quan | Cần sửa | "Số: 12/CV-UBND" |
| 3 | Nơi nhận | Thiếu mục "Lưu: VT" | Cần sửa | Thêm dòng cuối danh sách nơi nhận |
Điểm cần kiểm chứng: thẩm quyền ký TM./KT. theo quy chế của cơ quan bạn."

## Checklist tự kiểm
- [ ] Đã chạy review_vn_document với từng file .docx và trích kết quả nguyên văn.
- [ ] Mỗi lỗi có vị trí cụ thể và đề xuất sửa.
- [ ] Đã phân loại: bắt buộc / nên sửa / cần xác nhận.
- [ ] File gốc nguyên vẹn (kiểm tra kích thước hoặc tên không đổi).
- [ ] Số liệu cộng trừ đã tính lại (run_script hoặc tính trực tiếp), không kết luận bằng cảm nhận.

## Lỗi thường gặp
- Báo cáo chung chung ('thể thức chưa chuẩn') không nêu vị trí.
- Khẳng định điều luật sai/đúng khi không có nguồn.
- Sửa thẳng vào file gốc.
- Bỏ sót văn bản có nhiều phần/phụ lục (chỉ rà trang đầu).

## Giới hạn
- Chỉ rà và đề xuất; không ký, không duyệt, không gửi văn bản.
- Không khẳng định hiệu lực pháp luật khi chưa có tài liệu; ghi 'cần kiểm chứng'.
- Không ghi đè file gốc.
