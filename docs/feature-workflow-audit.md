# Rà soát 17 chức năng và trải nghiệm hoàn thành công việc

## Kết luận

Danh mục có 39 quy trình chuyên biệt (đếm bằng API thực tế), nhưng số bước không chứng minh nghiệp vụ đã hoàn chỉnh.
Các quy trình đã mô tả đầu vào, tác vụ, sản phẩm và tiêu chí; phần lớn tác vụ vẫn do AI thực hiện qua công cụ chung.
CV có renderer và cơ chế bảo toàn dữ liệu riêng; không thể coi các nghiệp vụ khác đã đạt cùng mức độ kiểm chứng.

## Nâng cấp đã triển khai

- Tất cả chức năng lưu bản nháp nhập liệu theo quy trình/bước trong trình duyệt; file đã tải lên được tham chiếu lại trong cùng phiên, file mới chọn nhưng chưa gửi cần chọn lại.
- Hiện điều kiện chuẩn bị và yêu cầu bàn giao riêng cho từng chức năng ngay bước đầu.
- Chỉ cho duyệt bước khi có phản hồi, đã đánh dấu đủ tiêu chí kiểm tra và có file mới đúng loại nếu bước hứa xuất file.
- Chụp trạng thái file trước chạy; file cũ không được dùng để chứng minh bước mới đã tạo sản phẩm.
- Có thể chỉnh đầu vào và chạy lại bước hiện tại, giữ file đã tải lên.
- Hiện file thay đổi của bước hiện tại, không giới hạn sáu file; màn hình bàn giao có mở file và tải xuống.
- Bổ sung hợp đồng đầu vào/giữ nguồn/phiên bản/bàn giao vào từng quy trình; không thêm bước AI vô nghĩa chỉ để tăng số bước.
- Không đổi ID/thứ tự bước hiện có, để tiếp tục các công việc đã lưu.

Các ô đánh dấu là xác nhận của người dùng, không phải kết quả kiểm chứng tự động.
Kiểm tra file mới chỉ chứng minh file tồn tại, có dung lượng và đúng loại; không tự chứng minh nội dung đúng.
Nhiều loại file trong một bước có thể là các lựa chọn đầu ra; bộ chặn yêu cầu có ít nhất một loại phù hợp, tiêu chí xác nhận chốt bộ file thực sự cần.

## Ma trận nghiệp vụ và phần cần xây tiếp

| Chức năng | Luồng đã có | Hợp đồng nghiệm thu/bàn giao mới | Còn thiếu để thành ứng dụng chuyên môn hoàn chỉnh |
|---|---|---|---|
| Văn thư NĐ 30 | Soạn mới, dựng lại bản nháp, rà, chốt ký | Giữ mẫu cơ quan, căn cứ có nguồn, Word và chỗ còn cần xác nhận | Kho mẫu có xem trước, ánh xạ từng trường, đối chiếu định dạng tự động rộng hơn |
| Văn bản Đảng | Soạn và rà dự thảo | Đúng hệ thống văn bản, hướng dẫn gốc, danh sách điểm chưa xác nhận | Bộ mẫu được đơn vị kiểm duyệt và bộ kiểm định riêng; không chỉ dựa vào lời nhắc AI |
| Tổng hợp báo cáo | Kiểm kê, đối chiếu, xử lý sai lệch, viết báo cáo | Đủ đơn vị, nguồn từng chỉ tiêu, công thức và sai lệch | Màn hình ánh xạ cột, xem nguồn từng ô, duyệt chênh lệch có trạng thái |
| Rà thể thức | Rà trước trình ký, so bản sau sửa | Vị trí lỗi, đề xuất, bản mới, lỗi còn mở | Xem Word song song và chấp nhận/từ chối từng thay đổi |
| Biên bản họp | Lập biên bản và rút giao việc | Ý kiến/kết luận tách rõ, giao việc có chủ trì/hạn hoặc chưa xác nhận | Trình xem nguồn gắn từng kết luận, quản lý nhiệm vụ sau họp, nhập âm thanh có kiểm chứng |
| Kế toán | Đối chiếu, làm sạch/biểu đồ, công nợ | Dòng nguồn/trùng/thiếu, tổng kiểm soát, nhật ký xử lý | Ánh xạ cột và xác nhận dòng trùng, bảng đối chiếu tương tác, kiểm công thức độc lập |
| Nhân sự | Hợp đồng hàng loạt, tuyển dụng, onboarding | Xem trước mẫu, lỗi từng dòng, danh sách tài liệu thành công/thất bại | Màn hình ánh xạ biến mẫu, dữ liệu bảng, tiến độ batch và tải lại riêng các dòng lỗi |
| Dự án | WBS/phụ thuộc/rủi ro, báo cáo tiến độ | Phạm vi rõ, đầu ra/người phụ trách/hạn, kỳ cập nhật | Bảng công việc có trạng thái, lịch phụ thuộc, cập nhật dữ liệu tiến độ qua các kỳ |
| Giáo án | Mục tiêu, 4 hoạt động, học liệu, slide, phiếu hàng loạt | Đủ thời gian, nhiệm vụ/sản phẩm/đánh giá, điều kiện lớp | Trình sửa từng hoạt động và xem giáo án/phiếu trước xuất, thư viện mẫu theo trường |
| Ra đề/chấm | Ma trận, đề/đáp án, mã đề, tổng hợp điểm | Ma trận-câu hỏi-điểm khớp, đáp án riêng, phép tính và mã đề được rà | Ngân hàng câu hỏi, sửa ma trận trực quan, chấm từng bài có bằng chứng và xử lý khiếu nại điểm |
| Gia sư | Chẩn đoán, gợi ý, làm bài, chữa, tự luyện | Phù hợp mức hiểu, lỗi có lý do, mục tiêu buổi sau | Bản đồ kỹ năng và tiến bộ theo thời gian, bài kiểm tra thích ứng đã chấm xác định |
| Ôn thi | Lịch, đề luyện, chấm/lỗi, điều chỉnh | Lịch khả thi, nguồn bài chấm, việc học tiếp | Theo dõi hoàn thành lịch, lịch sử lỗi theo dạng bài, biểu đồ tiến bộ nhiều buổi |
| Ngoại ngữ | Hội thoại văn bản, sửa viết, từ vựng/lịch ôn | Câu gốc-câu sửa-lý do, mục tiêu và nội dung luyện tiếp | Lặp lại ngắt quãng có trạng thái, ghi âm và đánh giá phát âm nếu triển khai hỗ trợ âm thanh |
| Viết bài/báo cáo | Dàn ý/nguồn, góp ý bản nháp | Giữ luận điểm, nguồn kiểm chứng, việc tác giả cần làm | Trình sửa theo đoạn, trích dẫn liên kết tới nguồn, lịch sử thay đổi; hiện không phải trình viết báo cáo hoàn chỉnh |
| Slide | Dàn ý, PowerPoint/notes, phản biện và kịch bản | Thông điệp, đủ dữ liệu, nguồn biểu đồ, phân bổ thời gian | Thư viện theme và preview thật, sửa nội dung từng slide, đo thời lượng luyện nói |
| CV | Mẫu, form theo mẫu, biên tập, PDF/HTML, thư/phỏng vấn | Giữ đủ bản ghi/ID, dữ kiện và mẫu, báo lỗi khi thiếu | So sánh trước/sau ngay trên form, biên tập trực tiếp nội dung đã viết lại, phê duyệt từng thay đổi |
| Tài chính cá nhân | Ngân sách, tiết kiệm/trả nợ, phân tích sao kê | Dữ liệu thật/giả định tách riêng, công thức và cập nhật thực tế | Bảng phân loại giao dịch có duyệt, theo dõi thực chi theo kỳ, bộ tính kịch bản độc lập |

## Thứ tự phát triển chuyên sâu đề xuất

1. Các màn hình ánh xạ dữ liệu và preview có bộ kiểm xác định: tổng hợp báo cáo, kế toán, hợp đồng hàng loạt.
2. Bộ mẫu thực và biên tập trực tiếp: văn thư, giáo án, slide; không dùng hình xem trước giả lập thay cho file xuất thực.
3. Dữ liệu xuyên nhiều lần sử dụng: dự án, gia sư, ôn thi, ngoại ngữ, ngân sách.
4. Bằng chứng nguồn và duyệt từng thay đổi: rà văn bản, biên bản, bài viết, chấm bài.

Không nên thêm đồng loạt các mẫu đẹp trước khi có cơ chế đối chiếu dữ liệu và kết quả; lỗi mất nội dung ở CV cho thấy cần kiểm cả hai.
