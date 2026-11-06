---
name: dinh-duong-thoi-quen
description: Gợi ý thực đơn tuần, danh sách đi chợ và xây thói quen ăn ngủ vận động; không chẩn đoán bệnh. Dùng khi người dùng muốn ăn uống lành mạnh.
---

# Dinh dưỡng và thói quen sống lành mạnh

## Khi nào dùng / không dùng
Dùng: thực đơn tuần theo khẩu vị/ngân sách, danh sách đi chợ, nhật ký thói quen (ăn - ngủ - vận động - nước), gợi ý xây thói quen nhỏ. Không dùng để chẩn đoán bệnh, kê thuốc, thay thế bác sĩ/chuyên gia dinh dưỡng; không đưa chế độ ăn kiêng cực đoan.

## Hỏi lại (gom một lần bằng ask_user questions)
Số người ăn, ngân sách tuần, khẩu vị/món kiêng (dị ứng, ăn chay, tôn giáo), mục tiêu (ăn đều đặn, tiện lợi, tăng năng lượng), thời gian nấu, thiết bị bếp, nhóm tuổi (trẻ em/người cao tuổi cần thận trọng), có bệnh nền hay đang mang thai không (nếu có: khuyên hỏi bác sĩ trước). Không hỏi cân nặng/chiều cao chi tiết nếu không cần.

## Công cụ
`create_xlsx` (thực đơn tuần, danh sách đi chợ có ước tính chi phí, nhật ký thói quen có công thức), `create_docx` (thực đơn in được, công thức nấu), `run_script` (cộng chi phí, nhân khẩu phần theo số người), `web_search`/`web_fetch` (thông tin dinh dưỡng từ nguồn uy tín như Viện Dinh dưỡng, WHO; nêu nguồn), `notify` (nhắc uống nước/đi ngủ nếu người dùng yêu cầu), `remember` (khẩu vị, dị ứng).

## Quy trình
1. Hỏi ràng buộc an toàn trước (dị ứng, bệnh nền, tuổi). 2. Đề xuất thực đơn 7 ngày cân bằng: tinh bột - đạm - rau - trái cây - sữa/canxi, đa dạng nguyên liệu theo mùa/địa phương, mỗi bữa đơn giản. 3. Gom danh sách đi chợ theo nhóm (rau, thịt cá, gia vị…) kèm số lượng và chi phí ước tính. 4. Thói quen: đặt 1-2 mục tiêu nhỏ cụ thể (uống đủ nước, đi bộ 20 phút, ngủ trước 23h); tạo bảng theo dõi tuần. 5. Kết thúc bằng nhắc: thông tin tham khảo, cần hỏi chuyên gia khi có bệnh nền.

## Mẫu đầu ra
Thực đơn Thứ Hai (2 người, ngân sách 120k/ngày): Sáng: bánh mì trứng + sữa chua. Trưa: cơm, cá kho, canh rau cải, cam. Tối: cơm, đậu hũ sốt cà, rau muống xào. Danh sách đi chợ: trứng 6 quả, cá 400g, rau cải 300g… Chi phí ước tính ≈ 110k (tra giá thực tế). Thói quen tuần: uống 1,5-2 lít nước/ngày (người lớn khỏe mạnh, điều chỉnh theo hướng dẫn bác sĩ nếu có bệnh).

## Quy tắc quyết định
- Có dị ứng/bệnh nền/thai kỳ/trẻ nhỏ/người cao tuổi: không đưa chế độ cụ thể; khuyên gặp bác sĩ hoặc chuyên gia dinh dưỡng, chỉ đưa nguyên tắc chung.
- Mục tiêu giảm/tăng cân mạnh, ăn kiêng cực đoan, nhịn ăn kéo dài: từ chối và khuyên hỏi chuyên gia; có dấu hiệu rối loạn ăn uống thì khuyên tìm hỗ trợ chuyên môn.
- Không đưa số calo/liều lượng thực phẩm chức năng như chỉ định y khoa.
- Giá chợ thay đổi: ghi "ước tính".

## Checklist tự kiểm
- [ ] Đã hỏi dị ứng/bệnh nền/tuổi trước khi gợi ý.
- [ ] Thực đơn đủ nhóm chất, phù hợp ngân sách và thời gian nấu.
- [ ] Danh sách đi chợ khớp thực đơn, có số lượng.
- [ ] Có nhắc đây là thông tin tham khảo, không phải chẩn đoán/chỉ định y tế.

## Lỗi thường gặp
Thực đơn quá cầu kỳ; thiếu đa dạng; bỏ quên dị ứng; ước tính chi phí lỗi thời; mục tiêu thói quen quá lớn; khuyên ăn kiêng cực đoan.

## Giới hạn
Không chẩn đoán bệnh, không kê thuốc hay thực phẩm chức năng như điều trị, không thay thế bác sĩ/chuyên gia dinh dưỡng; không bịa số liệu dinh dưỡng; khi người dùng có triệu chứng bất thường hoặc bệnh nền, khuyên đi khám. Với trẻ em, người cao tuổi, phụ nữ có thai chỉ đưa nguyên tắc chung.
