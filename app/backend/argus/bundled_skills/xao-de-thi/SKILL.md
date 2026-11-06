---
name: xao-de-thi
description: Tạo nhiều mã đề từ một đề trắc nghiệm .docx: xáo câu và đáp án, giữ định dạng, có bảng đáp án. Dùng khi giáo viên cần xáo đề.
---

# Xáo đề thi thành nhiều mã đề

## Khi nào dùng / không dùng
- Dùng: giáo viên có đề trắc nghiệm Word (.docx) và cần nhiều mã đề khác nhau, kèm bảng đáp án từng mã.
- Không dùng: đề chỉ có tự luận; file PDF/.doc/ảnh chụp (nhờ lưu lại thành .docx; ảnh scan phải gõ lại); đề chưa soạn (dùng `ra-de-ma-tran`).

## Hỏi lại (gom MỘT lần bằng ask_user với `questions`)
1. File đề gốc ở đâu (đã tải lên hay đường dẫn trong thư mục làm việc)? 2. Số mã đề (mặc định 4, tối đa 20) và mã bắt đầu (mặc định 101). 3. Xáo cả thứ tự câu hay chỉ xáo đáp án (mặc định xáo cả hai, trong từng phần). 4. Đề gốc có đánh dấu đáp án đúng (gạch chân, chữ đỏ, tô nền, in đậm) không? Nếu không, xin bảng đáp án dạng "1A 2C 3B …" cho tham số `dap_an`.

## Công cụ
- `shuffle_exam(path, so_ma_de, ma_de_bat_dau, giu_thu_tu_cau, dap_an)`: tool chính; sửa trực tiếp file gốc nên giữ phông chữ, bảng, hình, công thức. KHÔNG soạn lại đề bằng `create_docx`.
- `read_document`: đọc một mã đề kết quả để đối chiếu nhanh.
- `compare_documents(path_a, path_b)`: so sánh hai mã đề hoặc đề cũ/đề mới để chắc nội dung không đổi ngoài thứ tự.
- `convert_to_pdf(path)`: xuất PDF để in nếu giáo viên cần.
- `create_xlsx`: chỉ dùng nếu cần bảng đáp án theo mẫu khác.

## Quy trình
1. Xác nhận file .docx. 2. Hỏi gộp các thông tin còn thiếu. 3. Gọi `shuffle_exam`. 4. Đọc kết quả: số câu, số phần, cảnh báo. 5. Mở ít nhất một mã đề bằng `read_document`: số câu tuần tự, mỗi câu đủ đáp án, dòng "Mã đề" đã đổi. 6. Báo cho giáo viên: danh sách file mã đề, file bảng đáp án (.xlsx), mọi cảnh báo.

## Công cụ nhận diện được gì
- Câu bắt đầu "Câu 1." (hoặc "Bài 1", "Question 1"); đáp án A-F mỗi đáp án một dòng hoặc cùng một dòng, cách nhau bằng tab/dấu cách.
- "Cả A và B đều đúng", "Tất cả các đáp án trên", "Không có đáp án nào đúng" luôn giữ ở cuối.
- Câu chỉ đổi chỗ trong cùng một phần (PHẦN I, PHẦN II…). Câu tự luận, đúng/sai, điền khuyết giữ nguyên vị trí.
- Đề phát cho học sinh được xóa dấu đánh dấu đáp án; bảng đáp án các mã đề nằm trong file Excel riêng.

## Mẫu báo cáo cuối
"Đã tạo 4 mã đề (101-104) từ 40 câu trắc nghiệm (2 phần). File: de-ma-101.docx … de-dap-an.xlsx. Lưu ý: câu 12 và 13 dùng chung một đoạn ngữ liệu nên đã giữ nguyên vị trí (nếu cần xáo, tách phần)."

## Quy tắc quyết định
- Đề có nhóm câu dùng chung ngữ liệu: bật `giu_thu_tu_cau` hoặc cảnh báo giáo viên.
- Đề không đánh dấu đáp án: không đoán; xin đáp án; nếu chưa có, giao đề nhưng ghi rõ bảng đáp án có dấu "?".
- Cần nhiều hơn 20 mã đề: chạy nhiều lần với `ma_de_bat_dau` khác.

## Checklist tự kiểm
- [ ] Số mã đề đúng yêu cầu, mỗi mã đề một file Word, có file bảng đáp án.
- [ ] Các mã đề khác nhau về thứ tự câu hoặc đáp án.
- [ ] Không câu nào thiếu đáp án hay trùng số câu (đã mở kiểm tra một mã đề).
- [ ] Mọi cảnh báo đã báo lại cho giáo viên.

## Lỗi thường gặp
Đề gốc không đánh dấu đáp án (bảng đáp án có "?"); đáp án nằm trong bảng/hộp văn bản (không xáo được, báo giáo viên); câu dùng chung ngữ liệu bị tách; file .doc cũ hay PDF.

## Giới hạn
Không đoán đáp án đúng, không sửa nội dung câu hỏi, không gửi đề ra dịch vụ bên ngoài; chỉ xử lý trong thư mục làm việc. Đề thi là tài liệu thi cử: nhắc giáo viên bảo mật các mã đề.
