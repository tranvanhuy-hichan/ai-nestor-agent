# Phiên dịch YouTube trực tiếp

Mở **Công cụ → Phiên dịch YouTube trực tiếp**, hoặc `/f/youtube-translate`.
Dán link video, chọn 1–4 ngôn ngữ phụ đề. Mặc định **Xem tại đây** nhúng trình phát YouTube ngay phía trên phụ đề. Phát video, bấm bắt đầu, chọn chính tab Nestor và bật chia sẻ âm thanh tab. Khi bật giọng dịch, bấm **Mở cửa sổ giọng dịch** trước khi bắt đầu. Giọng phát trong cửa sổ riêng, không phát trong tab video đang được thu. Có thể thu nhỏ cửa sổ giọng dịch nhưng cần giữ nó mở.

Chọn **Tab riêng** nếu muốn nghe giọng phiên dịch: mở video ở tab YouTube riêng, chọn giọng, bấm bắt đầu và chia sẻ âm thanh tab YouTube. Chức năng không cần và không yêu cầu micro. Video không cho phép nhúng có thể chuyển sang chế độ này bằng nút trên khung phát.

Chrome/Edge trên máy tính hỗ trợ luồng chia sẻ tab này. Khả năng lấy âm thanh phụ thuộc trình duyệt; nếu người dùng chỉ chia sẻ hình ảnh, trang báo rõ để chọn lại. Ở chế độ Tab riêng, Nestor đề nghị loại tab của ứng dụng khỏi hộp chia sẻ để âm thanh dịch không bị nhận diện ngược lại. Chế độ Xem tại đây cho phép và ưu tiên chia sẻ tab hiện tại; giọng dịch đi qua phần tử audio của cửa sổ giọng dịch riêng. Không có cơ chế chuyển về phát trong tab video nếu cửa sổ giọng bị chặn hoặc đóng. Quyền chọn tab vẫn do người dùng quyết định.

## Xử lý

- Trình duyệt thu các đoạn âm thanh độc lập 3–8 giây bằng MediaRecorder, ưu tiên ngắt tại khoảng lặng. Chỉ âm thanh được gửi tới máy chủ; hình ảnh chia sẻ không được tải lên.
- Groq Whisper Large V3 Turbo nhận diện âm thanh. Cần cấu hình provider Groq có API key và quyền speech-to-text.
- Model API được chọn dịch bản chép sang các ngôn ngữ đích trong một yêu cầu. CLI providers không dùng cho luồng này. Đoạn trước được dùng làm ngữ cảnh; không gọi công cụ hoặc thực thi chỉ dẫn trong video.
- Giọng dịch tùy chọn được tạo qua Google TTS. Giọng đọc dùng một ngôn ngữ, tốc độ 1,15×. Có thể tắt/đổi giọng trong khi tiếp tục xem phụ đề.
- Không lưu âm thanh trên đĩa, không lưu bản chép vào lịch sử chat. Phụ đề nằm trong bộ nhớ trang và mất khi tải lại/rời trang; có thể xuất SRT trước khi rời.

Đây là dịch gần trực tiếp theo đoạn, không đồng bộ từng từ với trình phát. Thời gian phản hồi thêm phụ thuộc API. Chia đoạn có thể cắt ngang câu; không bảo đảm độ chính xác tuyệt đối với nhạc, nhiều người nói hoặc tiếng quá nhỏ. Giọng đọc có độ trễ thêm do tạo và phát âm thanh.

## Điều khiển và lỗi

Link video, ngôn ngữ nguồn/đích, model dịch, giọng đọc, tùy chọn theo dõi và trạng thái mở cài đặt và cách xem video được lưu trong localStorage của trình duyệt. F5 khôi phục cấu hình; chia sẻ âm thanh cần bấm bắt đầu và chọn lại tab. Không tự tiếp tục thu âm sau khi tải lại.

- Đang nghe thì khóa lựa chọn model và ngôn ngữ phụ đề để mỗi phiên nhất quán; giọng đọc vẫn đổi được.
- Dừng nghe sẽ tắt các track chia sẻ, xử lý nốt đoạn vừa thu và các đoạn đã xếp hàng. Rời trang hoặc tải lại hủy yêu cầu, dừng thu âm/phát tiếng và đóng cửa sổ giọng dịch.
- Bật Capture Handle API khi trình duyệt có hỗ trợ để xác minh nguồn thu: Xem tại đây phải chọn đúng tab video Nestor; Tab riêng không nhận tab Nestor. Từ chối chia sẻ cửa sổ/toàn màn hình. Nếu nguồn đổi sang tab không hợp lệ, dừng và hủy xử lý.
- Nếu trình duyệt chặn popup, hiển thị hướng dẫn và chưa cho bắt đầu chế độ có giọng nhúng. Có thể tắt giọng để chỉ dùng phụ đề. Đóng cửa sổ giọng khi đang nghe sẽ dừng giọng, giữ phụ đề tiếp tục; mở lại để nhận các đoạn dịch tiếp theo.
- Khi API lỗi/hết hạn mức, dừng thu và báo lỗi. Những phụ đề đã có được giữ để tải xuống.
- Khi dịch chậm hơn thu âm, dừng thu và giải quyết hàng chờ thay vì âm thầm bỏ qua các đoạn đã thu.
- Nếu giọng đọc chậm hơn video hoặc phát lỗi, ngừng giọng, báo trạng thái; phụ đề tiếp tục. Tắt rồi chọn lại giọng để nghe tiếp.

Mốc thời gian SRT tính từ lúc bắt đầu nghe, không phải thời gian gốc của YouTube. Tua video hay bắt đầu giữa video sẽ không tự đổi mốc này. Không có cơ chế tự dừng hoặc tua tab YouTube.

## Kiểm chứng

`tests/test_live_translate.py` kiểm tra chuỗi nhận diện/dịch, đoạn im lặng, bản dịch thiếu ngôn ngữ, đầu vào sai, hạn mức và giới hạn xử lý đồng thời. `tests/test_speech.py` kiểm tra phản hồi âm thanh và lỗi. Đã thử API thật với câu tiếng Việt tổng hợp; trình duyệt kiểm tra thu/đóng gói audio, phụ đề đa ngôn ngữ, phát MP3, xuất SRT và dọn tài nguyên.

Đã đo thử bằng Screen Capture thật của Chromium: cửa sổ giọng phát MP3 thì RMS của tab video im lặng vẫn bằng 0; phát MP3 trong tab video thì RMS lớn hơn 0. Đây là kiểm tra tách nguồn theo tab, không phải thuật toán khử giọng sau khi hai nguồn đã trộn.
