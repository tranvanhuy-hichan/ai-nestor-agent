---
name: ra-de-ma-tran
description: Ra đề kiểm tra theo ma trận, bảng đặc tả (CV 7991), kèm đáp án, thang điểm; tổng hợp điểm lớp. Dùng khi giáo viên cần đề.
---

# Ra đề, ma trận, đáp án và tổng hợp điểm

## Khi nào dùng
Giáo viên cần: ma trận + bảng đặc tả, đề (trắc nghiệm/tự luận/kết hợp), đáp án và thang điểm, bảng điểm lớp có xếp loại. Không dùng để tạo nhiều mã đề từ đề có sẵn (dùng `xao-de-thi`) hay soạn giáo án (`giao-an-gdpt-2018`).

## Hỏi lại (gom bằng ask_user questions)
Môn, lớp; thời gian; hình thức (trắc nghiệm / tự luận / kết hợp, vd 70% TN - 30% TL); phạm vi nội dung; tỉ lệ mức độ (mặc định nhận biết 40% - thông hiểu 30% - vận dụng 20% - vận dụng cao 10%); bộ sách; có cần nhiều mã đề không.

## Công cụ
- `read_document`: đọc đề cương/ma trận cũ.
- `create_docx`: xuất ma trận, đề, đáp án; `create_xlsx`: bảng ma trận/bảng điểm có công thức.
- `grade_summary(path, he_so, output_path)`: tính điểm trung bình theo hệ số và xếp loại từ bảng điểm Excel của lớp (đọc mô tả tham số của tool để dùng đúng dạng `he_so`).
- `shuffle_exam`: tạo nhiều mã đề từ đề trắc nghiệm đã soạn (skill `xao-de-thi`).
- `docx_fill_template`: in hàng loạt phiếu điểm/thông báo từ mẫu.

## Quy trình
1. Chốt thông số (mục Hỏi lại). 2. Lập ma trận: bảng chủ đề x mức độ, ghi số câu và điểm từng ô; tổng điểm = 10, tổng số câu khớp đề (xem `templates/ma-tran-de.md`). 3. Lập bảng đặc tả: mỗi ô ghi yêu cầu cần đạt cụ thể. 4. Viết câu hỏi bám đúng ô ma trận; trắc nghiệm có 1 đáp án đúng, 3 phương án nhiễu hợp lý (lỗi sai thường gặp của học sinh), độ dài đáp án gần nhau. 5. Viết đáp án, hướng dẫn chấm, thang điểm chi tiết cho tự luận (chia điểm từng ý). 6. Rà tổng điểm và độ phủ nội dung. 7. Xuất file `create_docx` (đề, đáp án, ma trận riêng). 8. Nếu có bảng điểm: chạy `grade_summary` và báo số học sinh từng loại.

## Mẫu đầu ra
Ví dụ đề Toán 8 (45 phút, 5 TN + 2 TL): ma trận ô "Phân tích đa thức" - Nhận biết 1 câu TN (0,5đ); Thông hiểu 1 TN (0,5đ) + TL1 (1,5đ); Vận dụng TL2 (2,0đ)... Tổng 10đ. Đáp án TL1: ý a) 0,75đ (đặt nhân tử chung), ý b) 0,75đ (kết quả).

## Quy tắc quyết định
- Điểm trắc nghiệm mỗi câu bằng nhau; tổng thang 10 (làm tròn đến 0,25 nếu cần).
- Câu vận dụng cao ≤ 10% và phải có đáp án rõ ràng, không đánh đố.
- Đề có nhiều mã đề: soạn 1 đề gốc có đánh dấu đáp án đúng (gạch chân) rồi dùng `shuffle_exam`.
- Đánh giá học sinh THCS/THPT theo Thông tư 22/2021/TT-BGDĐT (Tốt/Khá/Đạt/Chưa đạt, quy định điểm trung bình môn) — xác nhận lại quy định hiện hành (cần kiểm chứng); tiểu học theo Thông tư 27/2020.

## Checklist tự kiểm
- [ ] Tổng điểm ma trận = 10, tổng số câu khớp đề.
- [ ] Mỗi câu hỏi trỏ về một ô ma trận; không có kiến thức ngoài phạm vi.
- [ ] Mỗi câu TN có đúng một đáp án đúng; vị trí đáp án đúng phân bố đều A-B-C-D.
- [ ] Có đáp án + thang điểm chi tiết cho phần tự luận.
- [ ] Đã tạo file bằng `create_docx`; nếu có bảng điểm đã gọi `grade_summary`.

## Lỗi thường gặp
Tổng điểm lệch; câu hỏi không bám ma trận; đáp án nhiễu quá lộ; hai đáp án cùng đúng; "tất cả các đáp án trên" lạm dụng; đề dài hơn thời gian làm bài (ước lượng 1-1,5 phút/câu TN, 7-10 phút/câu TL).

## Giới hạn
Không chép đề thi/đề thi thử có bản quyền; không bịa số liệu thực tế; kiến thức môn khác nhau theo bộ sách: ghi rõ phạm vi để giáo viên xác nhận. Đề là bản nháp cần giáo viên duyệt trước khi dùng.
