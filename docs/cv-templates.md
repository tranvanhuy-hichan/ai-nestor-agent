# CV theo mẫu mystore

Nguồn mẫu: `mystore/components/cv/templates`, cùng `parts`, `lang`, `levels` và model `lib/cv`.
Các file đã được sao chép vào Nestor, không phụ thuộc đường dẫn hoặc dịch vụ mystore khi chạy.
Giữ các bố cục gốc; sửa lỗi nhãn mục trong mẫu Tech và giữ liên kết dự án khi chuẩn hóa dữ liệu.

## Sử dụng

Vào **Chức năng → CV và xin việc**. Chọn quy trình tạo hồ sơ hoặc sửa CV.
Ở bước **Viết CV chuyên nghiệp / Viết lại CV**, chọn một mẫu bắt buộc trong thư viện,
có thể tìm kiếm, xem lớn và xem thêm mẫu. Nội dung minh họa không dùng làm dữ liệu hồ sơ.
Sau khi chọn mẫu, thư viện thu gọn và hiện form theo các trường thực sự được bố cục đó sử dụng.
Người dùng nhập liên hệ, thêm từng kinh nghiệm/học vấn/kỹ năng/dự án; mục không có thì chọn bỏ qua.
Mẫu có highlights hoặc sở thích thì mới hiện các mục đó. Ảnh được thu nhỏ và tải lên riêng,
không nhét base64 vào lời nhắn AI. Bản nháp form được lưu trong trình duyệt để tiếp tục sau khi tải lại trang.
Có ba cách biên tập: chuyên nghiệp, ATS, nổi bật. AI sửa lời văn, tự viết giới thiệu từ dữ kiện,
giữ nguyên mốc thời gian/số liệu và không thêm mục đã bỏ qua. Sau xuất file có thể yêu cầu chỉnh tiếp.

AI truyền đúng ID mẫu cùng hồ sơ thật đến `create_cv`, nhận PDF A4, HTML xem/in và JSON dữ liệu.
Thư xin việc vẫn tạo bằng công cụ Word. CV tự ngắt sang nhiều trang A4 theo nội dung, giữ chữ dễ đọc, không cắt mất phần cuối
hoặc ép chữ nhỏ để vừa một trang. Công cụ báo số trang thực tế sau khi xuất PDF.

## Dựng và chạy

- `npm --prefix app/frontend run build`: dựng giao diện và renderer dùng chung React templates.
- Renderer tự chứa thư viện React tại `app/backend/nestor/cv_templates/render.mjs`.
- Backend cần Node.js trên PATH, Playwright và Chromium. Cài browser bằng
  `.venv/bin/python -m playwright install chromium` nếu chưa có Chrome/Chromium hệ thống.
- Docker đã bổ sung Node.js và Playwright Chromium; chưa kiểm thử build image trong thay đổi này.
- Bản desktop đóng gói renderer; máy chạy vẫn cần Node.js và Chromium.

Renderer chuẩn hóa dữ liệu, escape HTML qua React, bỏ ảnh ngoài (chỉ nhận ảnh data JPEG/PNG/WebP),
chặn tải tài nguyên ngoài khi xuất PDF và kiểm tra đường dẫn ghi qua cơ chế quyền có sẵn.
Preview và PDF dùng chung `CvDocument`, cùng kích thước A4, font Arial và màu mặc định của mẫu.


## Bảo toàn nội dung

Bộ chuẩn hóa không cắt ngầm chuỗi hoặc số lượng kinh nghiệm, dự án, kỹ năng.
`create_cv` đối chiếu dữ liệu AI với form gốc trong lịch sử người dùng của cùng phiên,
không dựa vào CV trước do AI tạo. Giữ tất cả bản ghi gốc, ghép bản biên tập bằng ID
hoặc tên định danh, giữ nguyên liên hệ/ngày tháng/liên kết và mục bỏ qua.
Nếu bản biên tập thiếu mục, nội dung trống hoặc thiếu số liệu/liên kết gốc,
công cụ báo lỗi trước khi xuất và yêu cầu AI hoàn thiện bản viết lại; không âm thầm thay
bằng nguyên văn. AI đọc lại dữ kiện và ID qua `read_cv_profile` nếu cần.
Độ dài câu không được dùng làm thước đo bảo toàn ý nghĩa: bản biên tập được phép ngắn hơn
khi diễn đạt tốt hơn. Công cụ giữ đủ cấu trúc và các mốc định lượng; việc giữ đủ mọi ý nghĩa
vẫn cần người dùng xem lại bản biên tập.
