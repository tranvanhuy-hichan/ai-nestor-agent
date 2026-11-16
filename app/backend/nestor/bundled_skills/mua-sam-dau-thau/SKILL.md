---
name: mua-sam-dau-thau
description: "So sánh báo giá nhà cung cấp, tính lại giá, kiểm tra hồ sơ dự thầu theo yêu cầu HSMT, soạn thư dự thầu nháp. Dùng cho mua sắm và đấu thầu."
---

# Mua sắm và đấu thầu

## Khi nào dùng / không dùng
- DÙNG: so sánh báo giá nhiều nhà cung cấp; tính lại thành tiền, thuế, tổng; lập bảng đối chiếu yêu cầu hồ sơ mời thầu (HSMT) với hồ sơ dự thầu; checklist hồ sơ; soạn thư dự thầu, bảng kê năng lực, thư làm rõ nháp; theo dõi hạn.
- KHÔNG dùng: quyết định nhà thầu trúng thầu, chấm điểm chính thức thay tổ chuyên gia, tư vấn pháp lý đấu thầu ràng buộc (phap-che), dự toán xây dựng đầu tư công (dau-tu-cong).
- Quy định đấu thầu thay đổi: điều khoản pháp luật chỉ nêu khi có trong tài liệu người dùng; còn lại 'cần kiểm chứng'.

## Hỏi lại (gom một lần bằng ask_user questions)
1. Bạn đóng vai bên mời thầu/chủ đầu tư hay nhà thầu; loại gói (hàng hóa, dịch vụ, xây lắp, tư vấn); hình thức (chào hàng, mua sắm trực tiếp, đấu thầu rộng rãi).
2. HSMT/yêu cầu báo giá và các hồ sơ/báo giá cần xem (thư mục).
3. Tiêu chí đánh giá, thang điểm, điều kiện loại; thời điểm đóng thầu.
4. Cách so giá: có/không VAT, chi phí vận chuyển, bảo hành, thời gian giao hàng.

## Công cụ
| Việc | Công cụ |
|---|---|
| Đọc HSMT, báo giá, hồ sơ năng lực (Word/PDF/scan) | read_document, view_image |
| Đối chiếu bảng báo giá, tính lại | excel_audit(path), run_script |
| Gộp báo giá nhiều nhà cung cấp về một bảng | excel_merge_reports(paths, output_path, header_hints) |
| So hai bản báo giá/hồ sơ | compare_documents(path_a, path_b) |
| Bảng so sánh, checklist | create_xlsx (tổng, thứ hạng bằng công thức) |
| Thư dự thầu, thư làm rõ, báo cáo so sánh | create_docx; văn bản nhà nước: vanban_types, vanban_write_docx |
| Hồ sơ lớn nhiều phần | team_run, delegate |
| Tìm quy định trong kho | kb_search |

## Quy trình so sánh báo giá
1. Đọc yêu cầu (thông số kỹ thuật, số lượng, điều kiện) và từng báo giá.
2. Chuẩn hóa về cùng cơ sở: đơn vị tính, quy cách, đã/chưa VAT, giao tại đâu, bảo hành, thời hạn giao, hiệu lực báo giá.
3. Tính lại: thành tiền = số lượng × đơn giá, tổng, thuế; dùng công thức. Sai số học trong báo giá nhà cung cấp: nêu rõ, không tự sửa số của họ.
4. Bảng so sánh: Hạng mục | NCC A | NCC B | NCC C | Thấp nhất (công thức) | Ghi chú đáp ứng kỹ thuật (Đạt/Không đạt/Cần làm rõ).
5. Kết luận: xếp hạng theo tiêu chí người dùng; nêu rủi ro (giá thấp bất thường, thiếu hạng mục, thời hạn). Đề xuất, KHÔNG chọn thay người có thẩm quyền.
6. Câu hỏi làm rõ gửi nhà cung cấp: liệt kê riêng.

## Quy trình kiểm tra hồ sơ dự thầu (đối chiếu HSMT)
1. Trích mọi yêu cầu bắt buộc từ HSMT (thư bảo đảm dự thầu, giấy phép, kinh nghiệm, nhân sự, tài chính, thời hạn hiệu lực, thành phần hồ sơ).
2. Lập checklist: Yêu cầu | Vị trí trong HSMT | Có trong hồ sơ? | Vị trí trong hồ sơ | Kết luận (Đạt/Thiếu/Không rõ) | Ghi chú.
3. Kiểm tra số liệu và nhất quán (giá trong đơn dự thầu so với bảng giá; ngày hiệu lực; chữ ký, đóng dấu theo mô tả).
4. Liệt kê điểm thiếu, hết hạn, mâu thuẫn và đề xuất bổ sung/làm rõ trước hạn.

## Mẫu đầu ra
- Workbook: 'So sánh giá' (công thức MIN, RANK) | 'Đối chiếu kỹ thuật' | 'Checklist hồ sơ' | 'Câu hỏi làm rõ'.
- Ví dụ: báo giá B ghi 12 bộ × 4.500.000 = 52.000.000 → tính lại 54.000.000, 'sai số học 2.000.000', ghi vào làm rõ.

## Quy tắc quyết định
- Giá thấp nhất chưa phải tốt nhất: luôn kèm trạng thái đáp ứng kỹ thuật và rủi ro.
- Thiếu hạng mục trong báo giá: coi là 'không so được', hỏi làm rõ, không cộng ước lượng.
- Mâu thuẫn HSMT: nêu cả hai vế, đề xuất hỏi bên mời thầu.
- Không đưa ra kết luận loại/trúng thầu; nêu kết quả đối chiếu và để người có thẩm quyền quyết định.

## Checklist tự kiểm
- [ ] Mọi phép tính giá được tính lại bằng công thức; số gốc của nhà cung cấp không bị sửa.
- [ ] Mỗi kết luận Thiếu/Không hợp lệ chỉ rõ yêu cầu và vị trí đã kiểm.
- [ ] Không có điều khoản luật nào chưa có nguồn.
- [ ] Các câu hỏi làm rõ được liệt kê riêng.
- [ ] Các báo giá đã được chuẩn hóa cùng cơ sở (VAT, đơn vị, giao hàng).

## Lỗi thường gặp
- So sánh giá khác cơ sở VAT/vận chuyển.
- Bỏ qua điều kiện hiệu lực, bảo hành.
- Bịa điều khoản của Luật Đấu thầu để kết luận.

## Giới hạn
- Không quyết định nhà thầu trúng, không nộp hồ sơ, không gửi thư, không thanh toán.
- Không bịa số, quy định. Thông tin hồ sơ dự thầu là bí mật: chỉ xử lý trong thư mục làm việc.
