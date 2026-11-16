---
name: ke-toan
description: "Làm sạch, đối chiếu, tổng hợp bảng Excel kế toán: kiểm tra công thức, công nợ, sổ vs sao kê, báo cáo, biểu đồ. Dùng khi có số liệu tài chính cần xử lý."
---

# Kế toán - Tài chính (bảng tính có công thức sống)

## Khi nào dùng / không dùng
- DÙNG: làm sạch bảng Excel lộn xộn; kiểm tra công thức, ô cộng sai, số lưu dạng chữ; đối chiếu sổ chi tiết với sao kê ngân hàng; bảng công nợ theo khách hàng; báo cáo thu chi, dashboard KPI, biểu đồ; mô hình tài chính đơn giản (dòng tiền, khấu hao, điểm hòa vốn).
- KHÔNG dùng: thay kế toán trưởng ký, quyết toán thuế, định khoản chính thức, tư vấn thuế/đầu tư cụ thể; dữ liệu dự toán xây dựng đầu tư công (dau-tu-cong).

## Hỏi lại (gom một lần bằng ask_user questions)
1. File dữ liệu ở đâu; kỳ báo cáo; đơn vị tiền tệ và đơn vị tính (đồng/nghìn/triệu).
2. Mục tiêu: làm sạch, đối chiếu, tổng hợp, hay lập biểu đồ/báo cáo.
3. Khóa đối chiếu (số chứng từ, ngày + số tiền, mã khách hàng); dung sai cho phép (mặc định 0).
4. Mẫu báo cáo/biểu mẫu của đơn vị (nếu có).

## Công cụ
| Việc | Công cụ |
|---|---|
| Kiểm tra file Excel: công thức lỗi, ô số dạng chữ, ô tổng không khớp, dòng trùng, cột lệch kiểu | excel_audit(path) |
| Đọc dữ liệu lớn, đối chiếu hai nguồn, pivot | run_script (pandas/openpyxl; chạy thử trên mẫu nhỏ) |
| Gộp nhiều file bảng giống nhau | excel_merge_reports(paths, output_path, header_hints) |
| Tạo file kết quả có công thức sống | create_xlsx (ô bắt đầu bằng '=' là công thức) |
| Báo cáo/slide tóm tắt | create_docx, create_pptx |
| So hai phiên bản bảng tính | compare_documents(path_a, path_b) |
| Xuất PDF | convert_to_pdf(path) |

## Quy trình
1. Mở file bằng excel_audit trước khi sửa: lấy danh sách vấn đề (vị trí sheet/ô, loại lỗi). KHÔNG sửa file gốc; làm trên bản sao.
2. Làm sạch có ghi chú: chuẩn hóa ngày (một định dạng), số (bỏ dấu cách/chữ thừa, nhận diện dấu thập phân/nghìn), loại khoảng trắng, thống nhất tên khách hàng/mã. Mọi sửa đổi ghi vào sheet 'Ghi chú sửa đổi': Ô cũ | Giá trị cũ | Giá trị mới | Lý do.
3. Đối chiếu: ghép theo khóa; nhóm kết quả: Khớp | Lệch số tiền | Chỉ có ở nguồn A | Chỉ có ở nguồn B | Nghi trùng. Số lệch được LIỆT KÊ trong sheet 'Chênh lệch', KHÔNG điều chỉnh để cho khớp.
4. Tổng hợp: dùng công thức (SUMIFS, COUNTIFS, VLOOKUP/XLOOKUP, tỷ lệ), không dán số cứng ở các ô tổng.
5. Biểu đồ: chọn loại phù hợp (đường theo thời gian, cột so sánh, tròn chỉ khi ít nhóm); ghi đơn vị và kỳ trên tiêu đề.
6. Chạy lại excel_audit trên file kết quả; tổng chi tiết = tổng cuối; sheet nguồn nguyên vẹn.
7. Báo: số dòng xử lý, số dòng lệch/chờ xác nhận, các giả định (định dạng ngày, dấu thập phân), việc cần kế toán trưởng xác nhận.

## Mẫu đầu ra
- Workbook: 'Dữ liệu gốc' (không đổi) | 'Đã làm sạch' | 'Tổng hợp' (công thức) | 'Chênh lệch' | 'Ghi chú sửa đổi'.
- Công nợ: Mã KH | Tên | Số dư đầu | Phát sinh có | Phát sinh nợ | Số dư cuối (= đầu + nợ - có, công thức) | Tuổi nợ.
- Ví dụ đối chiếu: sổ ngày 05/03 số tiền 12.500.000, sao kê ngày 06/03 12.500.000 cùng nội dung → 'Khớp (lệch 1 ngày, ghi chú)'; sao kê có giao dịch 3.200.000 không có trong sổ → 'Chỉ có ở sao kê'.

## Quy tắc quyết định
- Số lệch nhỏ (làm tròn): chỉ coi là khớp khi dung sai do người dùng nêu; nếu không, vẫn liệt kê.
- Ngày dạng mơ hồ (03/04): xác định theo toàn cột; nếu không thể, hỏi, không đoán.
- Trùng nghi vấn: không xóa, đánh dấu để người dùng quyết.
- Công thức cũ trong file người dùng: giữ nguyên trừ khi sai rõ ràng; ghi nhận trong ghi chú.

## Checklist tự kiểm
- [ ] Tổng trong bảng là công thức và khớp tổng chi tiết (excel_audit không báo ô tổng sai).
- [ ] Mọi sửa đổi được ghi trong sheet ghi chú; file gốc nguyên vẹn.
- [ ] Đơn vị tính ghi rõ; số lệch được liệt kê, không tự điều chỉnh.
- [ ] Đã nêu việc cần kế toán trưởng xác nhận và các giả định.
- [ ] Biểu đồ có tiêu đề, đơn vị, kỳ dữ liệu.

## Lỗi thường gặp
- Dán số cứng thay vì công thức; làm tròn trung gian làm lệch tổng.
- Trộn đơn vị (nghìn/triệu) giữa các sheet.
- Xóa dòng 'trùng' không kiểm tra; hiểu sai dấu thập phân.

## Giới hạn
- Không thay kế toán trưởng; không ký, không nộp báo cáo thuế, không điều chỉnh số để khớp.
- Không bịa số liệu; không tư vấn thuế/đầu tư cụ thể. Dữ liệu tài chính chỉ xử lý trong thư mục làm việc.
