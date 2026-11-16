---
name: nhan-xet-hoc-ba
description: Viết nhận xét học bạ, thư/thông báo phụ huynh, kế hoạch họp phụ huynh cho giáo viên chủ nhiệm; hỗ trợ in hàng loạt từ mẫu.
---

# Công tác chủ nhiệm: nhận xét học bạ, họp phụ huynh, thông báo

## Khi nào dùng / không dùng
Dùng: nhận xét từng học sinh (cuối kỳ/năm), thư/thông báo gửi phụ huynh, kế hoạch & biên bản họp phụ huynh, tổng hợp điểm lớp. Không dùng: ra đề (`ra-de-ma-tran`), soạn bài (`giao-an-gdpt-2018`).

## Hỏi lại (gom một lần bằng ask_user questions)
Cấp học (tiểu học / THCS / THPT); học kỳ hay cả năm; danh sách học sinh kèm dữ kiện quan sát (điểm mạnh, điểm cần cố gắng, tiến bộ) — file Excel/Word hoặc gõ trực tiếp; mẫu học bạ/mẫu thông báo của trường (nếu có); thông tin nhạy cảm cần tránh. Không có dữ kiện về một em thì KHÔNG bịa: ghi "…" để giáo viên điền.

## Công cụ
- `read_document`: đọc danh sách học sinh/mẫu của trường.
- `grade_summary(path, he_so, output_path)`: tính trung bình môn theo hệ số và xếp loại từ bảng điểm lớp; dùng số liệu này làm căn cứ nhận xét (không nhận xét trái với điểm).
- `docx_fill_template(template_path, data, data_path, output_dir, name_field)`: sinh hàng loạt file nhận xét/thư phụ huynh từ một mẫu Word và bảng dữ liệu (mỗi học sinh một file, đặt tên theo `name_field`).
- `create_docx` / `create_xlsx`: tài liệu đơn lẻ hoặc bảng tổng hợp.
- `convert_to_pdf`: xuất PDF để gửi phụ huynh nếu cần.

## Quy trình
1. Chốt cấp học và khung đánh giá: THCS/THPT theo Thông tư 22/2021/TT-BGDĐT (mức Tốt/Khá/Đạt/Chưa đạt; đánh giá phẩm chất, năng lực), tiểu học theo Thông tư 27/2020/TT-BGDĐT (Hoàn thành tốt / Hoàn thành / Chưa hoàn thành) — cần kiểm chứng văn bản hiện hành của địa phương.
2. Nhận dữ kiện từng em; nếu có bảng điểm, chạy `grade_summary` để lấy xếp loại.
3. Viết nhận xét theo công thức: Điểm nổi bật cụ thể (có bằng chứng quan sát) → Điều cần cố gắng (diễn đạt tích cực, hành động được) → Định hướng/lời động viên. 2-4 câu, mỗi em một nhận xét khác nhau (xem `templates/mau-nhan-xet.md`).
4. Với nhiều học sinh: dùng bảng dữ liệu + `docx_fill_template`; kiểm tra ngẫu nhiên 3 file.
5. Họp phụ huynh: soạn kế hoạch (mục đích, nội dung, thời gian, phân công), thư mời, biên bản mẫu (xem `templates/thu-phu-huynh.md`).
6. Rà checklist rồi giao file.

## Mẫu đầu ra
Tiểu học: "Em chăm chỉ, hoàn thành tốt các bài tập Toán; đọc trôi chảy và biết giúp đỡ bạn. Cần luyện chữ viết cẩn thận hơn. Cô tin em sẽ tiến bộ hơn nữa."
THCS: "Em có tinh thần học tập tốt, tích cực phát biểu ở môn Ngữ văn. Cần dành thêm thời gian ôn tập Toán để chắc kiến thức nền. Em nên duy trì thói quen đọc sách."

## Quy tắc quyết định
- Không dùng từ gán nhãn ("lười", "kém", "hư"); mô tả hành vi và cách cải thiện.
- Thông tin sức khỏe, hoàn cảnh gia đình: không đưa vào nhận xét công khai; nếu cần, đưa vào ghi chú riêng cho giáo viên.
- Xếp loại phải khớp với số liệu `grade_summary`.
- Dữ liệu học sinh là dữ liệu cá nhân của trẻ em: chỉ xử lý trong máy, không gửi ra dịch vụ ngoài.

## Checklist tự kiểm
- [ ] Mỗi nhận xét 2-4 câu, có điểm nổi bật cụ thể + hướng cố gắng.
- [ ] Các nhận xét không trùng nhau giữa các em (so sánh bằng mắt hoặc `run_script` nếu danh sách dài).
- [ ] Không bịa dữ kiện; chỗ thiếu ghi "…".
- [ ] Xếp loại khớp bảng điểm; đã gọi `grade_summary` nếu có điểm.
- [ ] Với hàng loạt: đã kiểm tra ít nhất 3 file sinh ra.

## Lỗi thường gặp
Nhận xét sao chép (cùng một câu cho nhiều em); chỉ khen chung chung; nêu điểm yếu mà không gợi hướng; lệch giữa nhận xét và xếp loại; lộ thông tin cá nhân; đặt tên file có dấu gây lỗi khi nén.

## Giới hạn
Không bịa dữ kiện về học sinh, không đưa thông tin nhạy cảm vào văn bản công khai, không so sánh học sinh này với học sinh khác trong văn bản gửi phụ huynh. Nhận xét là bản nháp để giáo viên duyệt và chịu trách nhiệm.
