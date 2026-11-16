---
name: quan-ly-du-an
description: "Chia việc, lập kế hoạch, bảng rủi ro, báo cáo tiến độ tuần/tháng cho dự án; chạy nhóm nhiều trợ lý cho hồ sơ lớn. Dùng khi quản lý tiến độ dự án."
---

# Quản lý dự án

## Khi nào dùng / không dùng
- DÙNG: lập kế hoạch (WBS, mốc, người phụ trách), phân việc, bảng rủi ro, theo dõi tiến độ từ bảng công việc, báo cáo định kỳ, biên bản và việc sau họp dự án, hồ sơ lớn cần chia nhiều trợ lý.
- KHÔNG dùng: thẩm định dự án đầu tư công (dau-tu-cong), dự toán chi phí xây dựng, thay quyết định của trưởng dự án.
- Ước lượng thời gian, nhân lực là ĐỀ XUẤT, không phải cam kết.

## Hỏi lại (gom một lần bằng ask_user questions)
1. Mục tiêu, phạm vi, mốc bắt buộc, ngày bắt đầu/kết thúc mong muốn.
2. Nguồn lực: danh sách người/vai trò, năng lực, số giờ mỗi tuần.
3. Dữ liệu hiện có: bảng công việc, báo cáo cũ, ràng buộc (ngân sách, phụ thuộc bên ngoài).
4. Báo cáo cho ai, tần suất, mẫu báo cáo; cách tính % tiến độ (theo công việc hoàn thành hay theo giờ).

## Công cụ
| Việc | Công cụ |
|---|---|
| Kế hoạch, bảng công việc, rủi ro, Gantt dạng bảng | create_xlsx (cột trạng thái, % bằng công thức, ngày kết thúc = bắt đầu + thời lượng) |
| Báo cáo tiến độ, biên bản, đề cương | create_docx; báo cáo gửi cấp trên theo NĐ 30: vanban_types, vanban_write_docx |
| Đọc kế hoạch/báo cáo cũ | read_document |
| Gộp báo cáo của nhiều nhóm | excel_merge_reports(paths, output_path, header_hints) |
| Chia vai chạy song song (hồ sơ lớn) | team_run, team_note_write, team_note_read, delegate |
| Việc dài chạy nền | task_start, task_status |
| So bản kế hoạch cũ - mới | compare_documents(path_a, path_b) |
| Kiểm tra bảng Excel | excel_audit(path) |

## Quy trình
1. Làm rõ mục tiêu và phạm vi (SMART); ghi giả định.
2. WBS: chia theo sản phẩm/giai đoạn, mỗi gói việc 1-5 ngày công, có sản phẩm đầu ra, người phụ trách, người phối hợp.
3. Phụ thuộc và đường găng: nêu rõ việc nào chờ việc nào; đánh dấu đường găng; dự phòng thời gian (đề xuất 10-20%, ghi rõ là đề xuất).
4. Bảng rủi ro: Rủi ro | Xác suất | Ảnh hưởng | Biện pháp phòng | Người theo dõi | Kích hoạt khi.
5. Theo dõi: % tiến độ lấy từ dữ liệu người dùng (số việc xong/tổng hoặc giờ); công thức tính trong Excel. Nêu việc chậm, nguyên nhân (nếu người dùng nêu), đề xuất biện pháp.
6. Báo cáo tuần: Tóm tắt (1-2 câu) | Đã làm | Kế hoạch tuần tới | Rủi ro/vướng mắc | Cần quyết định.
7. Hồ sơ lớn: dùng team_run (ví dụ: Soạn thảo, Số liệu, Trình bày, Rà soát) với bảng ghi chép chung, trưởng nhóm tổng hợp; báo trạng thái từng thành viên.

## Mẫu đầu ra
| STT | Gói việc | Phụ trách | Bắt đầu | Thời lượng (ngày) | Kết thúc (=công thức) | Phụ thuộc | % | Trạng thái |
Ví dụ: 'Thiết kế CSDL | An | 03/11 | 5 | =C+E | sau #2 | 40% | Đang làm'. Báo cáo tuần: 'Tiến độ chung 38% (6/16 gói xong, theo bảng công việc ngày 12/11); chậm 2 gói: …; cần quyết định: thêm người cho gói #7?'.

## Quy tắc quyết định
- Ước lượng thiếu cơ sở: đưa khoảng (tối thiểu - tối đa) và nêu rõ giả định.
- % tiến độ không có số liệu: không điền, ghi '……'.
- Xung đột nguồn lực: đề xuất 2 phương án, nêu hệ quả; việc quyết thuộc người dùng.
- Việc nhỏ (dưới 1 giờ): không tạo gói việc riêng.

## Checklist tự kiểm
- [ ] Mỗi việc có người phụ trách và ngày; % tiến độ lấy từ dữ liệu người dùng.
- [ ] Rủi ro có biện pháp và người theo dõi.
- [ ] Ước lượng được ghi rõ là đề xuất; giả định được liệt kê.
- [ ] Ngày kết thúc và % là công thức; excel_audit không báo lỗi.
- [ ] Quyết định cần người dùng đưa ra được nêu riêng.

## Lỗi thường gặp
- Kế hoạch lý tưởng không có dự phòng; bỏ qua phụ thuộc.
- Nhồi một người 150% công suất không nhận ra.
- Báo cáo mô tả hoạt động thay vì kết quả và rủi ro.

## Giới hạn
- Không tự giao việc cho người thật, không gửi báo cáo, không thay đổi hệ thống quản lý dự án.
- Không bịa tiến độ, số liệu, cam kết thay trưởng dự án.
