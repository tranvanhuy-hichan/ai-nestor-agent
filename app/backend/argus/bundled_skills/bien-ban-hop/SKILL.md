---
name: bien-ban-hop
description: "Lập biên bản họp, kết luận và danh sách giao việc có hạn từ ghi chú, gỡ băng hoặc ảnh sổ tay. Dùng sau cuộc họp, giao ban, hội nghị."
---

# Biên bản họp và giao việc

## Khi nào dùng / không dùng
- DÙNG: có ghi chú, văn bản gỡ băng, ảnh sổ ghi chép cuộc họp; cần biên bản đúng thể thức NĐ 30 (hoặc biên bản nội bộ doanh nghiệp), thông báo kết luận, bảng nhiệm vụ - người phụ trách - hạn.
- KHÔNG dùng: họp của cấp ủy cần thể thức Đảng (van-ban-dang-hd05); soạn chương trình họp/lịch (thu-ky).

## Hỏi lại (gom một lần bằng ask_user questions)
1. Cuộc họp gì, thời gian bắt đầu - kết thúc, địa điểm.
2. Chủ trì, thư ký, thành phần tham dự (có vắng mặt, có khách mời không).
3. Nguồn nội dung: file ghi chú/gỡ băng/ảnh ở đâu.
4. Biên bản cho cơ quan nhà nước (dùng BIEN_BAN NĐ 30) hay nội bộ doanh nghiệp (Word thường)?
5. Số, ký hiệu biên bản; có cần thêm thông báo kết luận gửi các đơn vị không.

## Công cụ
| Việc | Công cụ |
|---|---|
| Đọc ghi chú, gỡ băng, file Word | read_document |
| Ảnh sổ tay, ảnh bảng trắng | view_image (chép lại đúng chữ, chỗ không đọc được ghi [không rõ]) |
| Biên bản đúng NĐ 30 | vanban_types(document_type_key=BIEN_BAN), vanban_write_docx, review_vn_document |
| Thông báo kết luận gửi các đơn vị | vanban_write_docx với THONG_BAO |
| Bảng nhiệm vụ - hạn | create_xlsx (ngày hạn, cột 'Còn lại' dùng công thức) |
| Biên bản nội bộ doanh nghiệp | create_docx |
| Xuất PDF | convert_to_pdf(path) |

## Quy trình
1. Đọc toàn bộ nguồn trước khi viết. Ghi ra các mục: thời gian, địa điểm, thành phần, nội dung từng người nói, số liệu, kết luận, nhiệm vụ.
2. Phân biệt rõ: ý kiến thảo luận (ai nói gì, tóm tắt trung thực), kết luận của chủ trì, nhiệm vụ được giao. Không thêm ý không có trong nguồn.
3. Mỗi nhiệm vụ: Việc | Người/đơn vị phụ trách | Hạn. Thiếu thì '……' và đưa vào danh sách cần xác nhận.
4. Dựng BIEN_BAN: vanban_types lấy structure. Khối ký đặc biệt: THƯ KÝ bên trái, CHỦ TỌA bên phải, cùng một hàng (two_columns, role signature_authority 'THƯ KÝ'/'CHỦ TỌA' và signature_name). Biên bản không có place_date riêng (thời gian nằm trong nội dung).
5. review_vn_document; sửa mọi [LỖI].
6. Lập bảng nhiệm vụ .xlsx; nếu được đề nghị, soạn thông báo kết luận (THONG_BAO) gửi các đơn vị.
7. Báo người dùng: file, số nhiệm vụ, các chỗ cần xác nhận (tên, hạn, số liệu nghe không rõ).

## Mẫu đầu ra
Thân biên bản (theo structure BIEN_BAN): thời gian bắt đầu; địa điểm; thành phần tham dự; chủ trì; thư ký; nội dung (đánh số từng nội dung: 'Ông/bà … báo cáo …', 'Ý kiến thảo luận: …', 'Kết luận của chủ trì: …'); thời gian kết thúc; khối ký.
Bảng nhiệm vụ:
| STT | Nhiệm vụ | Phụ trách | Phối hợp | Hạn | Nguồn (phút/đoạn) |
Ví dụ: ghi chú 'phòng KT báo cáo thu ngân sách đạt 82%, đề nghị đôn đốc, hạn 20/10' → nhiệm vụ 'Đôn đốc thu ngân sách', phụ trách 'Phòng Kinh tế' (nếu họp nêu), hạn 20/10; số 82% chép nguyên.

## Lưu ý khi dùng công cụ rà cho biên bản
Biên bản theo NĐ 30 không có khối 'Nơi nhận' bắt buộc và khối ký là THƯ KÝ - CHỦ TỌA. Vì vậy:
- vanban_write_docx có thể CẢNH BÁO thiếu 'signature_name_left/signature_name_right': đây chỉ là tên nhãn trong cấu trúc, không phải role; khối ký THƯ KÝ/CHỦ TỌA bằng signature_authority + signature_name là đúng.
- review_vn_document có thể báo [LỖI] 'Nơi nhận' hoặc 'Thẩm quyền ký' với biên bản: coi là không áp dụng, nhưng BÁO LẠI cho người dùng thay vì im lặng; các lỗi khác vẫn phải sửa.
- Mẫu sẵn dùng: templates/bien-ban.paragraphs.json (BIEN_BAN), templates/bang-nhiem-vu.md.

## Quy tắc quyết định
- Nguồn có hai bản mâu thuẫn (ghi chú khác gỡ băng): nêu cả hai ở danh sách cần xác nhận, dùng bản gỡ băng làm chính.
- Không rõ ai nói: ghi 'một đại biểu', không gán tên đoán.
- Lời nói thô, lặp: gọn lại nhưng giữ đủ ý và số liệu.
- Nhiệm vụ do chính bạn suy ra (không ai giao): KHÔNG đưa vào danh sách chính thức, ghi riêng mục 'đề xuất thêm'.

## Checklist tự kiểm
- [ ] Mọi ý kiến, số liệu, tên người trong biên bản có trong nguồn.
- [ ] Mỗi nhiệm vụ có phụ trách và hạn, hoặc '……' kèm trong danh sách cần xác nhận.
- [ ] Khối ký THƯ KÝ - CHỦ TỌA cạnh nhau; review_vn_document không còn [LỖI] nào khác ngoài hai mục không áp dụng cho biên bản (Nơi nhận, Thẩm quyền ký) đã nêu ở trên.
- [ ] Phân biệt tách bạch thảo luận / kết luận / nhiệm vụ.
- [ ] Đã liệt kê chỗ nghe không rõ hoặc cần xác nhận.

## Lỗi thường gặp
- Biến ý kiến cá nhân thành kết luận.
- Thêm nhiệm vụ hoặc hạn không có trong cuộc họp.
- Sai thứ tự khối ký, hoặc để chữ ký đứng dọc.
- Ghi tên chức danh không đúng so với nguồn.

## Giới hạn
- Chỉ tạo bản dự thảo; chủ tọa và thư ký ký xác nhận.
- Không bịa lời phát biểu, số liệu, hạn; không gửi thông báo kết luận đi.
- Nội dung họp nhạy cảm chỉ xử lý trong thư mục làm việc.
