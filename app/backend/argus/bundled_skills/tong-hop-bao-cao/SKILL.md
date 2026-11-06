---
name: tong-hop-bao-cao
description: "Gộp báo cáo Excel/Word của nhiều đơn vị thành bảng tổng hợp và báo cáo chung, chỉ ra số liệu lệch, đơn vị chưa nộp. Dùng khi có từ 3 báo cáo trở lên."
---

# Tổng hợp báo cáo nhiều đơn vị

## Khi nào dùng / không dùng
- DÙNG: gộp báo cáo của các phường, trường, phòng ban (mỗi nơi một file, mẫu có thể khác nhau); đối chiếu số liệu giữa các báo cáo; tìm đơn vị chưa nộp; viết báo cáo chung từ dữ liệu đã gộp.
- KHÔNG dùng: chỉ rà một file (ra-soat-the-thuc), kế toán đối chiếu sổ sách (ke-toan), báo cáo đầu tư công có mẫu riêng (dau-tu-cong).

## Hỏi lại (gom một lần bằng ask_user questions)
1. Thư mục hoặc danh sách file nguồn; danh sách đơn vị kỳ vọng phải nộp (để phát hiện thiếu).
2. Kỳ báo cáo, đơn vị tính, chỉ tiêu bắt buộc phải có.
3. Có báo cáo mẫu/biểu mẫu chung không; báo cáo chung dùng thể thức nào (văn bản NĐ 30 hay báo cáo nội bộ).
4. Sai lệch bao nhiêu thì coi là cần báo (mặc định: mọi chênh lệch khác 0 giữa số chi tiết và số tổng do chính đơn vị ghi).

## Công cụ
| Việc | Công cụ |
|---|---|
| Liệt kê file nguồn | list_dir, glob |
| Gộp nhiều file Excel khác mẫu thành một bảng | excel_merge_reports(paths, output_path, header_hints) |
| Đọc báo cáo Word/PDF/ảnh scan | read_document, view_image |
| So hai phiên bản báo cáo của cùng đơn vị | compare_documents(path_a, path_b) |
| Việc đặc thù (chuẩn hóa tên cột lạ, lọc, pivot) | run_script (chạy thử trên 1-2 file trước) |
| Dựng bảng tổng hợp cuối có công thức | create_xlsx (ô '=' là công thức) |
| Dựng báo cáo chung đúng NĐ 30 | vanban_types, vanban_write_docx (BAO_CAO hoặc BAO_CAO_CO_BANG), review_vn_document |
| Từ 10 đơn vị trở lên | team_run chia nhóm đọc, bảng ghi chép chung |
| Xuất PDF | convert_to_pdf(path) |

## Quy trình
1. plan_set; list_dir để có danh sách file; so với danh sách đơn vị kỳ vọng, ghi ngay đơn vị chưa có file.
2. Đọc thử 2-3 file để hiểu cấu trúc, tên cột khác nhau giữa các đơn vị (STT, 'Tên chỉ tiêu', 'Số lượng'...).
3. excel_merge_reports với header_hints ánh xạ tên cột lệch về tên chuẩn. File không đọc được: ghi vào danh sách lỗi, KHÔNG bỏ qua im lặng.
4. Kiểm tra số học từng đơn vị: tổng các dòng con có khớp dòng tổng của chính file đó không; đơn vị tính có thống nhất không (triệu đồng/đồng, ha/m2).
5. Dựng bảng tổng hợp bằng công thức (SUM theo đơn vị/chỉ tiêu) và sheet 'Sai lệch': Đơn vị | Chỉ tiêu | Số báo cáo | Số tính lại | Chênh lệch | File, ô. Số gốc KHÔNG bị sửa.
6. Quét địa danh/cấp hành chính cũ (huyện, quận, tên phường đã sáp nhập) và liệt kê; nếu nhiều thì gợi ý skill chuan-hoa-sau-sap-nhap.
7. Viết báo cáo chung: nhận định chỉ dựa trên số trong bảng; mọi con số trong lời văn truy được về ô nguồn. Dựng file bằng vanban_write_docx rồi review_vn_document.
8. Báo người dùng: file, số đơn vị đã gộp/tổng, đơn vị chưa nộp, số chỗ lệch, việc cần họ xác nhận với đơn vị.

## Mẫu đầu ra
- Sheet 'Tổng hợp': hàng = chỉ tiêu, cột = đơn vị + cột Tổng (=SUM(...)).
- Sheet 'Sai lệch' như bước 5. Sheet 'Chưa nộp / lỗi đọc': Đơn vị | Tình trạng | Ghi chú.
- Báo cáo chung: I. Kết quả chung (số liệu tổng); II. Kết quả theo lĩnh vực/đơn vị nổi bật; III. Tồn tại, hạn chế (từ phần sai lệch, thiếu số liệu); IV. Kiến nghị.
- Ví dụ: 12 phường, 11 nộp; phường X ghi tổng 1.250 nhưng cộng các dòng ra 1.205 → sheet Sai lệch ghi chênh lệch 45 tại ô D14; báo cáo chung dùng số của chính phường và chú thích 'đã đề nghị xác nhận'.

## Quy tắc quyết định
- Hai đơn vị trùng chỉ tiêu nhưng khác đơn vị tính: quy đổi chỉ khi tên đơn vị tính ghi rõ; còn nghi ngờ thì để nguyên và đưa vào 'cần xác nhận'.
- Số tổng của đơn vị khác số cộng chi tiết: giữ cả hai, báo sai lệch, dùng số nào trong tổng hợp thì nói rõ (mặc định số cộng chi tiết, ghi chú).
- Ô trống: coi là 'không có số liệu', KHÔNG tự điền 0.
- Ngày nộp trễ hạn: chỉ nêu khi người dùng cho hạn.

## Checklist tự kiểm
- [ ] Mọi file nguồn có trong bảng hoặc trong danh sách lỗi đọc (đếm khớp tổng số file).
- [ ] Ô tổng trong .xlsx là công thức; tổng chi tiết khớp tổng cuối.
- [ ] Sheet 'Sai lệch' đủ cột và số gốc không bị sửa.
- [ ] Đã liệt kê đơn vị chưa nộp (so với danh sách kỳ vọng) và địa danh/cấp cũ.
- [ ] Mọi con số trong báo cáo chung truy được về ô nguồn.
- [ ] Báo cáo chung dựng bằng vanban_write_docx, review_vn_document không còn [LỖI].

## Lỗi thường gặp
- Cộng nhầm dòng tổng của đơn vị vào chính bảng (đếm đôi).
- Gộp hai chỉ tiêu tên gần giống nhưng khác nghĩa.
- Bỏ im lặng file đọc lỗi; sửa số cho 'khớp'.
- Viết nhận định định tính không có số liệu hỗ trợ.

## Giới hạn
- Không sửa số của đơn vị, không tự suy diễn số thiếu; chỉ báo sai lệch.
- Không gửi báo cáo, không nộp lên hệ thống thay người dùng.
- Số liệu nhạy cảm (dân cư, tài chính) chỉ xử lý trong thư mục làm việc.
