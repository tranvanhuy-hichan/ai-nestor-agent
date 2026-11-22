# start | Bắt đầu với Nestor

## Bài thực hành: từ mở Nestor đến câu trả lời đầu tiên
1. Bấm **Mở chức năng** ở đầu bài này để đến **Trang chủ**. Từ sidebar, mở **Quản trị → Mô hình AI**.
2. Mở **Model xử lý**, tìm nhóm nhà cung cấp bạn dùng, rồi bấm **Thêm** trên thẻ tương ứng.
3. Điền phần cấu hình của nhà cung cấp, chọn model, rồi dùng **Lưu thay đổi**. Nếu Ollama đã chạy nhưng danh sách trống, kiểm tra địa chỉ dịch vụ và model đã cài.
4. Mở **Trò chuyện**, chọn phiên mới và gửi `Hãy trả lời đúng một dòng: Nestor đã sẵn sàng.`
5. Nếu có câu trả lời, thử tiếp một yêu cầu có đầu ra rõ ràng, ví dụ `Viết email khoảng 100 từ bằng tiếng Việt để mời đồng nghiệp họp lúc 9 giờ.`
6. Nếu không có câu trả lời, đọc lỗi trong phiên. Kiểm tra lần lượt model đang chọn, khóa API hoặc Ollama, rồi gửi lại câu thử ngắn trước khi giao việc dài.

## Nên mở trang nào?
| Việc bạn muốn làm | Trang cần mở |
| --- | --- |
| Hỏi nhanh, viết nháp hoặc trao đổi nhiều lượt | Trò chuyện |
| Hỏi nhiều PDF, Word hoặc bảng tính và kiểm tra nguồn | Tài liệu |
| Giao việc mất nhiều phút | Tác vụ |
| Lặp một việc theo lịch | Tự động hóa |
| Viết và chỉnh nội dung theo từng khối | Sổ tay |

# chat | Trò chuyện

## Bài thực hành: đọc một tệp và tải kết quả
1. Vào **Trò chuyện** và mở một phiên mới để không lẫn ngữ cảnh với công việc cũ.
2. Bấm **+**, chọn một tài liệu nhỏ, rồi kiểm tra tên tệp xuất hiện cạnh ô soạn. Nếu chọn nhầm tệp, bỏ tệp đó khỏi lượt gửi trước khi tiếp tục.
3. Mở bộ chọn model cạnh ô soạn. Chọn model bạn vừa cấu hình. Với tài liệu nhạy cảm, kiểm tra model và quyền của phiên trước khi gửi.
4. Gõ `Đọc tệp đính kèm. Tóm tắt trong 5 gạch đầu dòng và tạo tệp tong-hop.md.` rồi bấm gửi. Nếu xuất hiện thẻ xác nhận thao tác, xem nội dung trước khi quyết định.
5. Đọc bản tóm tắt, mở bảng tệp của hội thoại, tìm `tong-hop.md` và dùng nút tải xuống. Nếu chỉ thấy câu trả lời trong chat, yêu cầu agent tạo tệp và báo tên tệp sau khi xong.
6. Nếu cần bản ngắn hơn, gửi `Giữ nguyên các số liệu, rút gọn mỗi ý còn một câu.` trong cùng phiên để agent dùng lại ngữ cảnh.

## Ví dụ yêu cầu
`Đọc hợp đồng đính kèm. Tạo bảng gồm điều khoản, thời hạn, bên chịu trách nhiệm và trang nguồn. Nếu thiếu thông tin, ghi “chưa thấy trong tài liệu”.`

## Khi kết quả chưa đúng
- Thêm tiêu chí đầu ra hoặc ví dụ mong muốn, rồi sửa tin nhắn cuối và gửi lại.
- Nếu model không đọc được tệp hoặc hình ảnh, kiểm tra loại tệp và model đang chọn. Với PDF scan, nạp vào **Tài liệu** và chạy OCR trước khi hỏi.

# tools | Công cụ chuyên trách

## Bài thực hành: chạy một biểu mẫu
1. Vào **Công cụ**, chọn thẻ có đầu ra phù hợp với việc bạn cần. Đọc nhãn các trường trước khi nhập.
2. Nếu thẻ có nhiều tab, chuyển sang tab đúng trước khi đính kèm. Đầu vào đã chọn cho một biểu mẫu có thể không áp dụng sang biểu mẫu khác.
3. Điền một bộ dữ liệu nhỏ trước. Với trường file, chọn đúng tệp rồi kiểm tra tên tệp. Với trường yêu cầu, nêu định dạng đầu ra, ngôn ngữ và các thông tin phải giữ nguyên.
4. Chọn model, bấm nút chạy của biểu mẫu và đợi kết quả. Mở vùng xem trước, sau đó tải hoặc sao chép kết quả nếu công cụ có nút tương ứng.
5. Nếu nút chạy chưa bấm được, kiểm tra trường bắt buộc và định dạng tệp. Nếu có lỗi từ model, thử cùng model bằng một câu nhắn ngắn trong **Trò chuyện** để kiểm tra kết nối.

## Khi công cụ báo lỗi
- Lỗi model hoặc khóa API: vào **Mô hình AI** để kiểm tra nhà cung cấp đang được chọn.
- Lỗi đọc tệp: thử mở tệp gốc. Với PDF chỉ chứa ảnh, chạy OCR trong **Tài liệu** trước khi yêu cầu agent đọc chữ.

# tasks | Tác vụ nền

## Bài thực hành: giao một việc có đầu ra rõ ràng
1. Vào **Tác vụ**, nhập tên tài liệu hoặc nguồn đầu vào, yêu cầu cụ thể và dạng kết quả vào ô giao việc.
2. Mở tùy chọn quyền nếu việc cần đọc hoặc tạo tệp. Chọn **Chỉ xem** khi chỉ cần tổng hợp thông tin.
3. Bấm **Giao việc**. Kiểm tra tác vụ xuất hiện trong danh sách và mở nó để xem trạng thái.
4. Nếu cần dừng, bấm **Dừng** trên tác vụ đang chạy. Đợi trạng thái cập nhật trước khi giao lại để tránh chạy trùng.
5. Khi kết quả đã có, đối chiếu với tiêu chí ban đầu. Nếu thiếu một phần, giao lại đúng phần đó, kèm tên đầu ra đã hoàn thành để agent có điểm tham chiếu.

## Ví dụ yêu cầu
`Tổng hợp báo cáo của ba phòng ban trong danh mục này. Trả về bảng số liệu chính, các điểm mâu thuẫn và nguồn cho từng kết luận.`

# kanban | Kanban

## Bài thực hành: tạo và giao một thẻ
1. Mở **Kanban**, bấm dấu **+** tại cột **Việc cần làm**.
2. Điền tiêu đề như `Rà soát hợp đồng A`. Trong mô tả, ghi nguồn, đầu ra và tiêu chí xong, rồi bấm **Thêm thẻ**.
3. Mở lại thẻ để rà nội dung. Nếu vừa chỉnh tiêu đề hoặc mô tả, bấm **Lưu** trước.
4. Bấm **Giao việc**. Mở lại thẻ để xem trạng thái hoặc chọn **Xem agent đã làm thế nào** khi liên kết xuất hiện.
5. Nếu thẻ bị chặn, đọc lỗi và dùng **Giao lại** khi nguyên nhân đã được xử lý. Nếu chỉ dùng bảng để theo dõi việc của mình, cập nhật cột của thẻ theo tiến độ công việc.

## Ví dụ thẻ
`Rà soát hợp đồng A. Đầu ra: bảng chi phí, mốc thanh toán, điều khoản phạt và trang nguồn. Hoàn tất khi đã kiểm tra đủ ba mục.`

# automations | Tự động hóa

## Bài thực hành: chạy báo cáo mỗi sáng
1. Vào **Tự động hóa → Tạo việc mới**.
2. Nhập tên `Tóm tắt việc mỗi sáng`. Trong **Mỗi lần chạy, agent cần làm gì?**, ghi nguồn cần xem và mẫu kết quả, ví dụ ba việc ưu tiên và các câu hỏi còn mở.
3. Trong **Khi nào chạy?**, chọn tần suất hằng ngày hoặc ngày trong tuần. Điền giờ chạy rồi đọc dòng mô tả lịch ngay bên dưới để kiểm tra.
4. Bật **Báo kết quả cho tôi** nếu muốn nhận thông báo. Nếu cần model riêng, mở **Tùy chọn nâng cao** và chọn trong **Dùng mô hình AI nào?**.
5. Bấm **Lưu**, sau đó bấm **Chạy thử** trên thẻ lịch. Mở **Tác vụ** hoặc **Hộp thư** để kiểm tra đầu ra.
6. Nếu chạy thử chưa đúng, mở thẻ để sửa nội dung yêu cầu rồi thử lại. Nếu bạn chỉ muốn kiểm tra lịch mà chưa muốn lặp, tạm dừng lịch sau khi thử.

## Ví dụ lịch
`Mỗi sáng, tóm tắt các việc chưa xong thành 3 ưu tiên. Cho biết việc nào cần tôi quyết định.`

# inbox | Hộp thư

## Bài thực hành: tìm kết quả vừa hoàn thành
1. Khi sidebar hiện số thông báo, mở **Hộp thư** và tìm thông báo mới nhất về tên tác vụ.
2. Bấm thông báo. Nếu có liên kết, mở tác vụ để xem kết quả hoặc lỗi đầy đủ.
3. Quay lại **Hộp thư**. Dùng **Đánh dấu đã đọc** để cập nhật số thông báo chưa đọc.
4. Dùng **Xóa hết** khi muốn bỏ các thông báo trong danh sách. Nếu bạn vẫn cần tên hoặc đường dẫn kết quả, ghi lại trước khi xóa.

# skills | Kỹ năng

## Bài thực hành: cài rồi thử một kỹ năng
1. Vào **Kỹ năng → Gợi ý cho bạn** hoặc **Khám phá ClawHub**. Gõ từ khóa liên quan đến việc cần làm.
2. Mở kỹ năng, đọc mô tả và phần yêu cầu. Nếu cần một CLI hay tài khoản khác, hoàn thành cấu hình theo phần hướng dẫn của kỹ năng.
3. Cài kỹ năng và chuyển về tab **Đã cài** để xác nhận nó xuất hiện. Nếu chưa thấy, kiểm tra bộ lọc đang chọn.
4. Mở **Trò chuyện**, gọi đúng tên kỹ năng và đưa một đầu vào nhỏ, ví dụ một đoạn văn thay vì cả tệp lớn.
5. Nếu tự viết kỹ năng, dùng **Tạo skill** trên trang Kỹ năng, điền nội dung hướng dẫn rồi kiểm tra lại bằng một phiên mới.

## Ví dụ
`Dùng kỹ năng tóm tắt tài liệu để rút gọn tệp đính kèm thành phần tóm tắt, các việc cần làm và câu hỏi còn mở.`

# notebook | Sổ tay

## Bài thực hành: tạo sổ tay và xuất Markdown
1. Mở **Sổ tay → Tạo sổ tay**. Bấm tiêu đề để đặt tên, ví dụ `Biên bản họp dự án`.
2. Trong vùng nội dung, gõ `/` để mở menu khối. Chọn tiêu đề cho từng mục, sau đó nhập ghi chú hoặc chèn bảng.
3. Nếu cần tách nội dung, chèn trang con, đặt tiêu đề và bấm **Tạo và chèn**.
4. Xem trạng thái lưu trên đầu ghi chú. Nếu lưu lỗi, dùng thao tác thử lại trước khi đóng trang.
5. Để xuất, bấm nút **Xuất Markdown** trên thanh ghi chú. Mở tệp tải xuống để kiểm tra nội dung cần chia sẻ.

## Ví dụ ghi chú họp
- Tạo ba mục: **Quyết định**, **Việc cần làm**, **Câu hỏi còn mở**.
- Dán ghi chú thô và yêu cầu chat nhóm nội dung theo ba mục đó, giữ nguyên tên người phụ trách và ngày đã thống nhất.

# documents | Tài liệu và trích dẫn

## Bài thực hành: hỏi trên một danh mục và kiểm chứng câu trả lời
1. Vào **Tài liệu → Tạo danh mục**, nhập `Hợp đồng dự án` rồi bấm **Tạo**.
2. Mở danh mục. Bấm **Chọn file** để nạp hai tệp hoặc **Chọn thư mục** nếu tài liệu đã nằm chung một thư mục. Để thử lần đầu, dùng một tệp PDF có chữ và một tệp DOCX nhỏ.
3. Mỗi tệp tối đa **60 MB**. Đợi tải xong rồi kiểm tra từng dòng. Nếu trạng thái còn **Đang xử lý**, chờ lập chỉ mục. Nếu thấy **Chỉ lưu file**, bạn vẫn mở hoặc tải bản gốc, tùy định dạng.
4. Trong chat bên phải, hỏi `Hai hợp đồng có thời hạn thanh toán khác nhau thế nào? Nêu tên tệp, thời hạn và nguồn của từng nhận định.`
5. Bấm một trích dẫn. Kiểm tra khung trái mở đúng tệp, cuộn tới trang hoặc đoạn liên quan và tô sáng chữ khớp. Dùng mũi tên ở đầu khung để về danh sách.
6. Nếu muốn xem bố cục trước khi hỏi, bấm ngay tên tệp hoặc dùng **⋮ → Xem file gốc**. Dùng nút tải trên đầu khung để lấy bản gốc.
7. Nếu cần báo cáo tổng hợp dài, quay về danh sách, bấm **Phân tích tài liệu**, ghi chủ đề cần tập trung và mở **Tác vụ** để đọc khi xong.

## Ví dụ yêu cầu
`Trong các hợp đồng của danh mục này, hợp đồng nào yêu cầu thanh toán trong 30 ngày? Lập bảng và trích nguồn từng dòng.`

## Khi không tìm được đoạn cần đọc
- PDF scan: mở menu tệp và chọn **Chạy OCR** nếu tài liệu chưa có chữ đọc được.
- Tìm kiếm chỉ theo từ khóa: thử từ khóa chính trong văn bản, rồi kiểm tra bộ embedding ở **Mô hình AI** nếu muốn tra cứu theo nghĩa.
- Word mở trực tiếp trong trình duyệt. Ngắt trang có thể khác Word trên máy; dùng tệp tải xuống để đối chiếu bố cục in.

Dùng menu **⋮** trên thẻ danh mục để đổi tên hoặc xóa. Xóa danh mục sẽ xóa cả tài liệu bên trong.

# ocr | OCR cho PDF scan

## Bài thực hành: nhận dạng một PDF scan tiếng Việt
1. Mở **Cài đặt → OCR** và xem lần lượt các trạng thái **Tesseract**, **Tiếng Việt** và **Tiếng Anh**.
2. Nếu thiếu Tesseract, bấm **Cài OCR tự động** khi nút có sẵn. Trên Windows, nếu trình cài hiện yêu cầu xác nhận quyền, xử lý trên máy đang chạy Nestor. Nếu nút cài không dùng được, mở **Hướng dẫn cài thủ công** trong cùng tab.
3. Nếu đã có Tesseract mà thiếu ngôn ngữ, bấm **Tải bộ ngôn ngữ tự động**. Sau khi cài thủ công, bấm **Kiểm tra lại**. Đợi trạng thái **OCR sẵn sàng**.
4. Vào **Tài liệu**, mở danh mục rồi tải lên PDF scan. PDF mới tự xử lý trang thiếu lớp chữ. Với tệp đã tải từ trước, bấm **⋮ → Chạy OCR**.
5. Đợi trạng thái lập chỉ mục kết thúc. Hỏi một cụm từ dễ kiểm chứng trong bản scan, ví dụ tên cơ quan hoặc thời hạn. Bấm nguồn để kiểm tra vùng tô sáng trên ảnh gốc.
6. Nếu không thấy chữ, xem ghi chú dưới tên tệp, mở ảnh trang để kiểm tra độ mờ hoặc hướng xoay và thử bản scan rõ hơn. Nếu vừa bổ sung ngôn ngữ, dùng **Chạy OCR** cho tệp cũ.

## Khi OCR cho kết quả sai
- Kiểm tra trang có bị xoay, cắt chữ hoặc mờ không. Bản scan rõ và đúng chiều giúp nhận dạng chính xác hơn.
- Sau khi cài bổ sung ngôn ngữ, chạy lại OCR cho tài liệu đã tải nếu trang trước đó chưa được nhận dạng.

# models | Mô hình AI và embedding

## Bài thực hành: tải embedding Ollama và đổi model
1. Mở **Mô hình AI → Model embedding** rồi bật tìm kiếm theo nghĩa nếu đang tắt.
2. Chọn **Trên máy bạn (Ollama)**. Bấm thẻ model muốn dùng, ví dụ `bge-m3`.
3. Nếu model chưa cài, bấm **Tải model tự động** và chờ tiến độ kết thúc. Nếu tải báo lỗi, mở **Hướng dẫn cài thủ công**, sao chép lệnh và chạy trên máy có Ollama.
4. Khi model báo **Đã cài**, bấm **Lưu thay đổi**. Kiểm tra dòng **Đang áp dụng trong hệ thống** để xác nhận đúng model.
5. Nếu đổi model cho dữ liệu cũ, bấm **Lập lại chỉ mục** sau khi đã lưu. Đợi tiến độ kết thúc và xem số đoạn đã lập chỉ mục.
6. Mở một danh mục đã biết nội dung và hỏi cùng một câu bằng cách diễn đạt khác với văn bản. Kiểm tra nguồn trả về trước khi dựa vào kết quả.

## Cấu hình model xử lý
- Thêm nhà cung cấp, điền thông tin xác thực nếu có và chọn model phù hợp. Đặt làm model chính rồi lưu.
- Thử lại bằng một câu ngắn trong chat. Với các việc cần đọc ảnh, chọn model hỗ trợ ảnh hoặc cấu hình model xem ảnh trong Cài đặt.

## Cấu hình embedding
- Với Ollama, khởi động dịch vụ trên máy chạy Nestor, chọn model và bấm **Tải model tự động**. Nếu cần, sao chép lệnh thủ công, chẳng hạn `ollama pull bge-m3`.
- Đợi trạng thái **Đã cài**, bấm **Lưu thay đổi**, rồi dùng **Lập lại chỉ mục** nếu đổi model.
- Nếu báo không kết nối được, kiểm tra dịch vụ Ollama. Nếu model có tên đúng nhưng chưa tải, kiểm tra danh sách model đã cài.

# extensions | Tiện ích và kết nối

## Bài thực hành: kết nối một MCP server
1. Mở **Kết nối → MCP server → Thêm MCP server**.
2. Đặt tên dễ nhận diện. Chọn loại kết nối mà dịch vụ yêu cầu, rồi điền địa chỉ hoặc cấu hình do dịch vụ cung cấp.
3. Dùng nút thử kết nối nếu có. Với dịch vụ cần OAuth, lưu cấu hình, hoàn tất đăng nhập và quay lại kiểm tra trạng thái.
4. Khi kết nối thành công, thử một thao tác đọc nhỏ trong chat. Kiểm tra tên công cụ và kết quả trước khi giao việc có ghi dữ liệu.
5. Nếu kết nối lỗi, xem lại địa chỉ, quyền tài khoản và trạng thái đăng nhập. Dùng **Kết nối lại** trên mục tương ứng sau khi sửa.

## Khi không kết nối được
- Kiểm tra ứng dụng đã được cấp quyền, token còn dùng được và địa chỉ dịch vụ đúng.
- Nếu vừa đổi thông tin xác thực, cập nhật kết nối trong Nestor trước khi thử lại.

# assistant | Hồ sơ, tính cách và trí nhớ

## Bài thực hành: tạo và thử một hồ sơ
1. Mở **Hồ sơ trợ lý → Tạo hồ sơ**.
2. Đặt tên theo vai trò, ví dụ `Trợ lý rà soát hợp đồng`. Viết chỉ dẫn gồm nhiệm vụ, giọng văn và giới hạn công việc.
3. Chọn model và các công cụ cần thiết trong biểu mẫu. Bấm **Lưu** rồi kiểm tra hồ sơ xuất hiện trong danh sách.
4. Dùng một yêu cầu nhỏ để thử. Nếu đầu ra không theo định dạng mong muốn, mở lại hồ sơ và thêm một ví dụ đầu ra.
5. Vào **Tính cách & trí nhớ** nếu cần chỉnh chỉ dẫn chung của workspace. Giữ yêu cầu chỉ dùng một lần trong chính phiên chat.

## Ví dụ hồ sơ
`Trợ lý rà soát hợp đồng: trả lời bằng tiếng Việt, ưu tiên bảng, ghi rõ trang nguồn và đánh dấu mục cần luật sư xem lại.`

# monitoring | Thống kê và hệ thống

## Bài thực hành: tìm nguyên nhân một lượt chat bị lỗi
1. Ghi lại thời điểm và model của lượt lỗi. Mở **Thống kê** để kiểm tra hoạt động quanh thời điểm đó.
2. Xem model và trạng thái thao tác. Nếu một công cụ báo lỗi, ghi tên công cụ và phần thông báo liên quan.
3. Mở **Sức khỏe hệ thống**, kiểm tra tài nguyên và nhật ký quanh cùng thời điểm. Nếu lỗi do một dịch vụ ngoài, ưu tiên kiểm tra dịch vụ đó.
4. Sau khi sửa cấu hình, gửi một yêu cầu ngắn bằng đúng model vừa lỗi. Xác nhận trả lời bình thường trước khi chạy lại việc lớn.

# settings | Cài đặt và bảo mật

## Bài thực hành: đổi màu và thử một thay đổi cần lưu
1. Mở **Cài đặt**, gõ `giao dien` rồi chọn thẻ **Giao diện**.
2. Trong hộp thoại, đổi **Bảng màu**. Màu cập nhật ngay. Đóng hộp thoại rồi mở lại để kiểm tra giá trị mới.
3. Mở **Cài đặt** và chọn **Bộ nhớ & Ngữ cảnh**. Nếu chỉ muốn thử thao tác lưu, chỉnh một giá trị dễ nhận biết rồi chọn **Bỏ thay đổi** để kiểm tra nó trở về giá trị trước đó.
4. Khi muốn áp dụng thật, chỉnh giá trị rồi bấm **Lưu thay đổi** ở dưới hộp thoại. Mở lại mục để xác nhận giá trị đã lưu.
5. Nếu muốn kiểm tra OCR hoặc model tìm kiếm, tìm `ocr` hoặc `embedding` ngay trong Cài đặt để mở hộp thoại tương ứng.

## Ví dụ bảo mật
- Nếu truy cập Nestor qua mạng nội bộ, vào **An toàn & Bảo mật** để đặt mật khẩu giao diện.
- Xem thiết lập xác nhận lệnh shell trước khi cấp cho phiên chat quyền chạy lệnh hoặc ghi tệp.

# backup | Sao lưu và khôi phục

## Bài thực hành: sao lưu trước khi chuyển máy
1. Mở **Cài đặt → Sao lưu & Khôi phục**.
2. Bấm **Tải bản sao lưu (.tar.gz)**. Đợi trình duyệt tải xong, kiểm tra tệp có trong thư mục tải xuống và ghi lại ngày tạo.
3. Lưu tệp vào vị trí bạn truy cập được từ máy mới. Trước khi khôi phục trên một máy đã có dữ liệu, tạo thêm một bản sao lưu của máy đích nếu dữ liệu đó cần giữ.
4. Trên máy đích, mở **Sao lưu & Khôi phục**, bấm **Khôi phục từ file** rồi chọn tệp vừa chuyển. Đối chiếu tên tệp trước khi xác nhận.
5. Đợi thông báo thành công và trang tải lại. Mở thử một hội thoại, một danh mục tài liệu và **Mô hình AI** để kiểm tra.
6. Nếu khôi phục nhầm bản, tìm bản sao dự phòng được tạo trước lúc khôi phục và kiểm tra ngày của tệp trước khi dùng lại.

## Sao lưu
- Tạo bản sao khi chuẩn bị chuyển máy, nâng cấp hoặc đổi cấu hình quan trọng.
- Tải tệp sao lưu xuống và lưu ở nơi bạn còn truy cập được nếu máy chủ gặp sự cố. Ghi lại thời điểm của bản sao.

## Khôi phục và kiểm tra
- Chọn đúng tệp, đọc hộp thoại xác nhận rồi bắt đầu khôi phục.
- Khi trang tải lại, kiểm tra một cuộc trò chuyện, danh mục tài liệu và cấu hình model để xác nhận dữ liệu đúng thời điểm mong muốn.
- Nếu chọn nhầm bản, tìm bản sao dự phòng Nestor tạo ngay trước khi khôi phục để quay lại.
