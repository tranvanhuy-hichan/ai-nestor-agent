# Chất lượng tài liệu bàn giao

Áp dụng yêu cầu nội dung đầy đủ vào cổng chất lượng của trợ lý, dùng cả khi chạy form và chat tự do.
Các bước tạo sản phẩm trong 39 quy trình có hướng dẫn kiểm kê đầu vào, lập cấu trúc, viết đầy đủ và đọc lại file.

- Báo cáo: mục tiêu/bối cảnh, dữ liệu có nguồn, phương pháp, phân tích và giải thích kết quả, hạn chế/giả định, kiến nghị phù hợp. Không áp máy móc cấu trúc báo cáo cho giấy mời/thư ngắn.
- Excel: đủ bản ghi/cột/đơn vị; công thức, tổng kiểm soát và sai lệch theo nghiệp vụ; hướng dẫn cập nhật; giữ nguồn và không tự thêm số liệu giả.
- PDF: đối chiếu bản nguồn, kiểm nội dung sau chuyển đổi, ngắt trang và chữ tiếng Việt; PDF dạng ảnh cần đọc ảnh/OCR để xác nhận.

## Kiểm tra thực tế

Tool `review_deliverable` mở DOCX/XLSX/PDF thật, trả metrics, errors và warnings.
Có thể yêu cầu các phần bắt buộc và số từ phù hợp loại tài liệu.
Đọc cả bảng Word; rà workbook chỉ tiêu đề, các lỗi ô và tham chiếu #REF!; PDF không đọc được không được báo thành công.
File mẫu trống chỉ được miễn kiểm nội dung khi có yêu cầu phù hợp.

Ở 17 chức năng trong danh mục, trước phản hồi cuối, agent kiểm lại các DOCX/XLSX/PDF mới hoặc thay đổi trong lượt đó.
File nguồn trong uploads và file cũ không thay đổi không bị coi là sản phẩm mới.
Phát hiện lỗi cấu trúc nghiêm trọng sẽ yêu cầu model sửa tối đa hai lần; còn lỗi thì phát sự kiện lỗi, không xác nhận hoàn tất.
Các file vẫn giữ lại để người dùng xem và chỉnh tiếp, không bị xóa.

Giới hạn: ngưỡng tự động mặc định 20 từ chỉ bắt sản phẩm rỗng/cộc lốc rõ ràng, không chứng minh tài liệu đã phân tích sâu.
Độ đầy đủ chuyên môn phụ thuộc cấu trúc, yêu cầu đối chiếu nguồn và kiểm tra của từng nghiệp vụ.
Không có phép đếm từ nào xác minh được tính đúng đắn của phân tích. Bộ kiểm không tính lại công thức Excel và không xác minh căn cứ pháp lý.


## Word native

Yêu cầu mới của các trợ lý dùng `create_docx(blocks=...)`: dựng heading, paragraph/runs,
bullets/numbered và table trực tiếp qua WordprocessingML/python-docx. Không chuyển Markdown
thành tài liệu cho các phiên trợ lý mới. API `content` cũ còn để tương thích với khách cũ.
Bảng có hàng tiêu đề lặp khi qua trang; kiểu chữ, heading, lề A4 và số trang được quản lý tập trung.
Văn bản hành chính vẫn dùng bộ dựng thể thức riêng; tài liệu từ mẫu vẫn dùng `docx_fill_template`.
