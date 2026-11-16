# Đánh giá Sổ tay so với Notion cá nhân offline

Ngày rà soát: 16/11/2026. Phạm vi: một người dùng, dữ liệu cục bộ, không cần chia sẻ, phân quyền nhóm hay đồng bộ đám mây. Đây là đánh giá mã nguồn và các thay đổi đã kiểm chứng, không phải cam kết đã có toàn bộ Notion.

## Hiện trạng

| Nhóm chức năng | Trạng thái thực tế |
| --- | --- |
| Tài liệu phân cấp | Có tạo, đổi tên, tài liệu con, breadcrumb, liên kết tới tài liệu khác |
| Soạn thảo | Có heading 1–3, đậm, nghiêng, code/code block, danh sách, checklist, quote, đường kẻ; undo/redo qua phím tắt của editor |
| Bảng | Chỉ là bảng nội dung; chưa có giao diện sửa hàng/cột, chưa phải database |
| Lưu trữ | Markdown và metadata trong workspace/pages; ghi thay thế nguyên tử; tự lưu sau 800 ms, thử lại khi lỗi |
| Tìm kiếm | Tìm tiêu đề và nội dung, hỗ trợ tìm không dấu; chưa có bộ lọc nâng cao |
| Ảnh | Đã bổ sung dán clipboard, kéo thả, chọn nhiều ảnh; lưu file trong workspace/pages/assets; hỗ trợ PNG/JPEG/GIF/WebP, tối đa 10 MB mỗi ảnh |
| Biểu tượng/logo | Có emoji và ảnh logo tải lên, hiển thị trong cây, breadcrumb và tiêu đề; bấm logo để gỡ |
| Di chuyển | Backend có kiểm tra vòng lặp cha/con; chưa có giao diện di chuyển/sắp xếp |
| AI | Có khung chat và công cụ đọc/ghi; có thể cần mạng tùy model/provider, không phải điều kiện để ghi chú thủ công |
| Offline | Ghi chú và ảnh tải lên hoạt động khi frontend và backend đang chạy trên máy, không cần Internet; chưa hỗ trợ PWA khi backend tắt |
| Xuất dữ liệu | File Markdown có thể sao chép thủ công cùng thư mục assets; chưa có luồng xuất/nhập và đổi đường dẫn ảnh tự động |

## Phần còn thiếu để đáp ứng nhu cầu Notion cá nhân

1. **Bảo vệ dữ liệu:** thùng rác/khôi phục thay cho xóa vĩnh viễn; lịch sử phiên bản, khôi phục bản cũ; bản nháp bền vững khi đóng tab/mất kết nối; xử lý ghi đồng thời và bản sửa từ AI. Hiện tự lưu chưa đảm bảo phục hồi khi đóng trình duyệt đột ngột.
2. **Tổ chức:** yêu thích, gần đây, di chuyển/sắp xếp cây, sao chép tài liệu, khóa sửa, template, liên kết ngược, liên kết tới block và mục lục.
3. **Editor:** menu `/`, kéo thả/sắp xếp block, toggle, callout, nhiều cột, màu chữ/nền, công thức toán, chỉnh bảng, caption/kích thước ảnh, file đính kèm. Markdown hiện tại cần được mở rộng hoặc bổ sung JSON block có phiên bản để giữ đúng cấu trúc phức tạp.
4. **Database:** property kiểu text/number/date/select/multi-select/checkbox/file; nhiều view table/board/calendar/list/gallery/timeline; filter/sort/group; relation, rollup, formula; template bản ghi. Không thể thay bằng bảng Markdown thông thường.
5. **Nhập/xuất và sao lưu:** nhập Markdown/HTML/CSV cùng ảnh, xuất Markdown/HTML/PDF, backup toàn bộ workspace và thử khôi phục. Cần đổi URL `/api/pages/assets/...` thành đường dẫn tương đối khi xuất.
6. **Hoàn thiện offline:** đóng gói desktop, kiểm tra tài nguyên nhúng không phụ thuộc CDN, xác định rõ dữ liệu lưu ở đâu, sao lưu định kỳ; tìm kiếm không cần dịch vụ ngoài.

Ưu tiên triển khai: bảo vệ dữ liệu → tổ chức và editor → database → nhập/xuất và hoàn thiện trải nghiệm. Database cần thiết kế lưu trữ/query riêng (ví dụ SQLite) trước khi xây các view.

## Giới hạn của thay đổi ảnh hiện tại

Ảnh tải lên được giữ độc lập với tài liệu để không xóa nhầm tài nguyên dùng chung. Chưa có thu gom ảnh không còn sử dụng. Kiểm tra loại ảnh bằng chữ ký file, không có bước giải mã/tái mã hóa. Ảnh chèn từ URL bên ngoài trong Markdown có sẵn vẫn cần mạng; muốn dùng offline phải tải ảnh lên máy. Thay đổi kích thước ảnh chưa được lưu như thuộc tính block riêng.

## Đối chiếu nguồn

- https://www.notion.com/help/images-files-and-media
- https://www.notion.com/help/views-filters-and-sorts
- https://www.notion.com/help/use-pages-offline
- https://www.notion.com/help/export-your-content
