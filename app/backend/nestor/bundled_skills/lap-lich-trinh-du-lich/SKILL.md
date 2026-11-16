---
name: lap-lich-trinh-du-lich
description: Lập lịch trình du lịch theo ngày với ngân sách, thời gian di chuyển và phương án dự phòng. Dùng khi người dùng lên kế hoạch chuyến đi.
---

# Lên lịch trình du lịch

## Khi nào dùng / không dùng
Dùng: lịch trình theo ngày, ước tính ngân sách, danh sách chuẩn bị. Không tự đặt vé/phòng hay thanh toán; không hứa giá, giờ mở cửa chính xác nếu chưa tra.

## Hỏi lại (gom một lần bằng ask_user questions)
Điểm đến, ngày đi - về (hoặc số ngày), số người và độ tuổi (có trẻ nhỏ/người lớn tuổi?), ngân sách tổng, phương tiện, phong cách (nghỉ dưỡng/khám phá/ẩm thực), điều kiện sức khỏe, nơi xuất phát.

## Công cụ
`web_search`/`web_fetch` (giờ mở cửa, giá vé, thời tiết, tình trạng giao thông; luôn kèm nguồn và ngày tra), `create_xlsx` (lịch trình + ngân sách có công thức), `create_docx` (lịch trình in được, danh sách đồ), `run_script` (cộng chi phí, thời gian di chuyển), `notify` (nhắc giờ khởi hành nếu yêu cầu), `remember` (sở thích).

## Quy trình
1. Chốt ràng buộc cứng (ngày, ngân sách, người đi). 2. Nhóm điểm đến theo khu vực địa lý để giảm di chuyển. 3. Mỗi ngày: sáng - trưa - chiều - tối, ghi giờ dự kiến, thời gian di chuyển (cộng đệm 20%), chi phí ước tính. 4. Mỗi ngày có 1 phương án mưa/dự phòng. 5. Ngân sách: vé, ăn uống, đi lại, lưu trú, dự phòng 10% — bảng xlsx có công thức tổng. 6. Danh sách chuẩn bị (giấy tờ, thuốc, thời tiết). 7. Rà checklist; ghi rõ mọi giá/giờ là ước tính cần xác nhận lại.

## Mẫu đầu ra
Ngày 1 Đà Nẵng: 8:00 Ăn sáng mì Quảng (~50k/người) → 9:00 Bà Nà Hills (vé cần kiểm tra giá hiện hành; di chuyển ~45 phút) → 17:30 Cầu Rồng → Dự phòng mưa: Bảo tàng Chăm. Tổng ngày 1 ≈ … (công thức). Xem `templates/lich-trinh-ngay.md`.

## Quy tắc quyết định
- Có trẻ nhỏ/người lớn tuổi: ít điểm hơn, nghỉ trưa dài, tránh lịch sáng sớm khuya.
- Ngân sách thấp: ưu tiên điểm miễn phí, ăn địa phương, di chuyển công cộng.
- Giá/giờ/thời tiết: tra nguồn, ghi ngày tra; không chắc thì ghi "cần xác nhận".
- Đi nước ngoài: nhắc kiểm tra visa/giấy tờ theo cơ quan chức năng.

## Checklist tự kiểm
- [ ] Mỗi ngày có giờ, thời gian di chuyển và phương án dự phòng.
- [ ] Tổng ngân sách ≤ ngân sách người dùng (có xlsx với công thức).
- [ ] Giá/giờ có nguồn và ngày tra hoặc ghi "cần xác nhận".
- [ ] Có danh sách chuẩn bị; không tự đặt vé/phòng.

## Lỗi thường gặp
Xếp quá nhiều điểm; bỏ quên thời gian di chuyển; không tính giờ cao điểm/ngày lễ; giá cũ; không có dự phòng mưa.

## Giới hạn
Không tự đặt vé, phòng, thanh toán; không bịa giá, giờ mở cửa, quy định visa; thông tin an toàn/dịch bệnh lấy từ nguồn chính thức; lịch là gợi ý, người dùng tự quyết định và xác nhận lại trước khi đi.
