---
name: van-thu-den-di
description: "Tóm tắt, phân loại văn bản đến, lập sổ theo dõi hạn xử lý và cảnh báo quá hạn, soạn đôn đốc. Dùng khi có lô văn bản đến/đi cần xử lý."
---

# Văn thư đến/đi và đôn đốc

## Khi nào dùng / không dùng
- DÙNG: một lô văn bản đến (file Word/PDF/ảnh hoặc danh sách) cần tóm tắt, phân loại độ khẩn, đề xuất người xử lý, theo dõi hạn; sổ theo dõi; công văn đôn đốc đơn vị trễ hạn; tóm tắt buổi sáng 'việc nào gấp, ai giữ, trễ bao lâu'.
- KHÔNG dùng: soạn văn bản trả lời chi tiết (van-thu-nd30), tổng hợp số liệu báo cáo (tong-hop-bao-cao).

## Hỏi lại (gom một lần bằng ask_user questions)
1. Lô văn bản ở đâu (thư mục) hoặc có sổ theo dõi cũ không (để cộng dồn).
2. Hôm nay là ngày nào (dùng cho tính hạn); cách tính hạn (ngày làm việc hay ngày thường; hạn ghi trong văn bản).
3. Danh sách người/phòng xử lý và phân công thường lệ (nếu có).
4. Có cần đăng nhập hệ thống quản lý văn bản để lấy văn bản không (chỉ đọc; xem Giới hạn).

## Công cụ
| Việc | Công cụ |
|---|---|
| Liệt kê và đọc văn bản | list_dir, read_document, view_image (bản scan) |
| Tính hạn, trạng thái quá hạn/sắp đến hạn từ sổ theo dõi | deadline_report(path, today) |
| Dựng sổ theo dõi .xlsx có công thức hạn | create_xlsx (cột 'Còn lại' = hạn - hôm nay, công thức) |
| Văn bản từ hệ thống điều hành (chỉ đọc) | browser_open, browser_snapshot, browser_text, browser_screenshot |
| Công văn đôn đốc | vanban_types, vanban_write_docx (CONG_VAN), review_vn_document |
| Việc lặp lại mỗi sáng | gợi ý người dùng tạo lịch tự động bằng nút Lịch tự động |

## Quy trình
1. list_dir lấy toàn bộ lô; đọc từng văn bản bằng read_document. File không đọc được: ghi vào sổ với trạng thái 'không đọc được', KHÔNG bỏ qua.
2. Với mỗi văn bản trích: số, ký hiệu, ngày ban hành, cơ quan gửi, trích yếu, hạn xử lý (nếu có), độ khẩn (hỏa tốc/khẩn/thường theo nội dung văn bản).
3. Phân loại: nhóm nội dung (chỉ đạo, báo cáo, mời họp, đề nghị phối hợp, thông báo), cần trả lời hay chỉ để biết.
4. Đề xuất hướng xử lý (đề xuất, kèm lý do ngắn) và người/phòng gợi ý; không tự giao việc.
5. Lập sổ .xlsx: STT | Số/ký hiệu | Ngày | Cơ quan | Trích yếu | Độ khẩn | Hạn | Còn lại (công thức) | Đề xuất | Phụ trách (đề xuất) | Trạng thái. Chạy deadline_report(path, today) để lấy danh sách quá hạn/sắp đến hạn trong N ngày.
6. Tóm tắt buổi sáng: 3 khối: Quá hạn, Sắp đến hạn (3 ngày), Mới đến cần xử lý.
7. Khi đơn vị trễ hạn: soạn công văn đôn đốc bằng vanban_write_docx (CONG_VAN) từ danh sách trễ hạn; để '……' số hiệu và ngày.

## Mẫu đầu ra
Tóm tắt buổi sáng:
- QUÁ HẠN (2): Công văn 214/UBND-VP (hạn 03/12, trễ 2 ngày) - đề xuất Phòng VH-XH trả lời; …
- SẮP ĐẾN HẠN (3): …
- MỚI ĐẾN (5): … (độ khẩn, đề xuất)
Ví dụ: văn bản ghi 'báo cáo trước ngày 10/12/2026', hôm nay 12/12 → 'trễ 2 ngày (theo lịch)'; nêu rõ cách tính (ngày thường).

## Quy tắc quyết định
- Văn bản không ghi hạn: để trống hạn, ghi 'không nêu hạn', không tự đặt.
- Hạn tính theo ngày làm việc hay ngày thường: dùng đúng cách người dùng nói; mặc định ngày thường và ghi chú.
- Hỏa tốc/khẩn: chỉ gán khi có dấu hiệu trong chính văn bản (đóng dấu, ghi chú), không suy từ nội dung.
- Văn bản mật: nhắc người dùng xử lý theo quy định, không trích nội dung ra ngoài tóm tắt cần thiết.

## Checklist tự kiểm
- [ ] Mọi văn bản trong lô có mặt trong sổ, kể cả file đọc lỗi (đếm khớp).
- [ ] Cột 'Còn lại' là công thức hoặc tính từ ngày hôm nay đã nêu rõ.
- [ ] Đã chạy deadline_report cho sổ và nêu số văn bản quá hạn.
- [ ] Đề xuất xử lý được nêu là đề xuất kèm lý do.
- [ ] Không có thao tác nào đổi trạng thái trên hệ thống thật.

## Lỗi thường gặp
- Tính hạn sai do nhầm năm/ngày (đọc 'ngày 03/12' là năm trước); luôn dùng ngày ban hành làm mốc để suy năm.
- Bỏ sót văn bản scan.
- Tự đánh dấu 'đã xử lý' hoặc chuyển xử lý.

## Giới hạn
- Chỉ đọc, tóm tắt, phân loại, đề xuất. KHÔNG đánh dấu đã xử lý, chuyển xử lý, ký số, phát hành trên hệ thống; thao tác thay đổi phải do người dùng xác nhận.
- Không bịa số, ngày, người nhận. Không gửi công văn đôn đốc.
