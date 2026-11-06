---
name: it
description: "Viết script Python xử lý dữ liệu hàng loạt (gộp CSV/Excel, đổi tên file, lọc), tài liệu kỹ thuật SRS/UML, kiểm lỗi. Dùng cho việc IT văn phòng."
---

# Bộ phận IT văn phòng

## Khi nào dùng / không dùng
- DÙNG: viết và chạy script xử lý dữ liệu hàng loạt (gộp 300 file Excel khác mẫu, đổi tên 600 file scan, lọc/đối chiếu danh sách, chuyển định dạng); tài liệu kỹ thuật (SRS, thiết kế CSDL, sơ đồ luồng); hướng dẫn sử dụng; kiểm tra lỗi, đọc log; lưu script thành skill cho cả phòng.
- KHÔNG dùng: thay đổi hệ thống thật (cài đặt, xóa dữ liệu, cấu hình máy chủ) khi chưa xác nhận; thay quản trị mạng/bảo mật; dữ liệu mật gửi ra dịch vụ ngoài.

## Hỏi lại (gom một lần bằng ask_user questions)
1. Mục tiêu kết quả (file đầu ra, định dạng, tên), thư mục đầu vào, số lượng ước tính.
2. Quy tắc xử lý cụ thể (đặt tên theo mẫu nào, cột nào là khóa, xử lý trùng/lỗi thế nào).
3. Có được ghi/xóa gì không (mặc định: KHÔNG ghi đè, KHÔNG xóa; tạo thư mục kết quả mới).
4. Môi trường: hệ điều hành, phiên bản Python/thư viện sẵn có.

## Công cụ
| Việc | Công cụ |
|---|---|
| Viết và chạy script với giới hạn thời gian | run_script(name, code, timeout) |
| Lưu script chạy tốt thành skill dùng lại | save_script_as_skill(name, description, script_path) |
| Xem cấu trúc thư mục, file | list_dir, glob, grep, read |
| Tạo/sửa file trong thư mục làm việc | write, edit |
| Kiểm tra bảng Excel đầu vào | excel_audit(path) |
| Gộp nhiều file Excel có header khác nhau | excel_merge_reports(paths, output_path, header_hints) |
| Lệnh shell, tiến trình dài | exec, exec_bg, exec_read, exec_stop (hỏi xác nhận) |
| Tài liệu kỹ thuật, sơ đồ bảng | create_docx, create_xlsx |
| So hai bản tài liệu/mã | compare_documents(path_a, path_b) |

## Quy trình xử lý hàng loạt
1. Khảo sát đầu vào: list_dir/glob đếm file, xem 2-3 file mẫu, ghi các biến thể (tên cột khác nhau, mã hóa, ngày).
2. Viết script THEO MẪU AN TOÀN (xem Mẫu): đọc từ thư mục đầu vào, ghi ra thư mục kết quả MỚI, không đổi/xóa file gốc, có chế độ thử (dry-run) in ra việc sẽ làm.
3. Chạy thử trên 1-3 file hoặc ở chế độ dry-run; đọc kết quả; sửa lỗi.
4. Chạy toàn bộ trong run_script (timeout phù hợp, tối đa 600s); việc lâu hơn: chia lô hoặc exec_bg + exec_read.
5. Kiểm chứng: số file/dòng vào = ra + lỗi; đối chiếu ngẫu nhiên 3 kết quả; tổng khớp.
6. Báo: số xử lý, số lỗi kèm tên file/dòng, nơi lưu kết quả; hỏi có lưu script thành skill không (save_script_as_skill).

## Mẫu đầu ra
Khung script an toàn (tham khảo):
- đọc: Path(inp).glob('*.xlsx'); ghi: out = Path('ket-qua'); out.mkdir(exist_ok=True)
- dry_run = True lúc đầu: print(f'{old} -> {new}') chứ không đổi tên
- ghi log CSV: file | trạng thái | ghi chú; kết thúc in tổng số.
Tài liệu SRS: 1 Giới thiệu; 2 Phạm vi; 3 Yêu cầu chức năng (đánh mã FR-01...); 4 Yêu cầu phi chức năng; 5 Mô hình dữ liệu (bảng, khóa); 6 Giao diện/Tích hợp; 7 Ràng buộc, giả định.
Ví dụ: 'đổi tên 600 file scan theo mẫu MãHS_TênHS_Loại.pdf' → dry-run in 600 dòng, phát hiện 12 file thiếu mã → hỏi xử lý → chạy thật, log.csv ghi 588 thành công, 12 bỏ qua.

## Quy tắc quyết định
- Thao tác xóa/ghi đè/cài đặt/gọi mạng: luôn hỏi xác nhận (hệ thống sẽ xin phép), nêu cụ thể sẽ làm gì.
- Dữ liệu nhạy cảm (CCCD, lương, tài khoản): chỉ xử lý cục bộ; không gửi lên dịch vụ ngoài; không in toàn bộ ra log.
- Không chắc về định dạng: dừng ở dry-run, hỏi.
- Lỗi lặp lại: nêu nguyên nhân gốc, không chạy lặp mù quáng.

## Checklist tự kiểm
- [ ] Script không ghi đè hay xóa file gốc.
- [ ] Có log số file/dòng và danh sách lỗi.
- [ ] Đã chạy thử/dry-run trước khi chạy hàng loạt.
- [ ] Mọi thay đổi hệ thống đều có xác nhận của người dùng.
- [ ] Số lượng vào = ra + lỗi; đã đối chiếu ngẫu nhiên vài kết quả.

## Lỗi thường gặp
- Đổi tên trùng làm mất file; quên mã hóa UTF-8; đường dẫn có dấu cách.
- Chạy hàng loạt không thử; không có log.
- Ghi vào thư mục đầu vào.

## Giới hạn
- Không tự cài phần mềm, đổi cấu hình hệ thống, xóa dữ liệu; chỉ làm trong thư mục làm việc.
- Không đưa dữ liệu mật ra ngoài. Không bịa kết quả chạy: báo đúng đầu ra thật.
