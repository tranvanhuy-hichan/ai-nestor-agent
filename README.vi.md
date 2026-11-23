<p align="center"><img src="docs/assets/nestor-cli-wordmark.svg" alt="Nestor Agent" width="880"></p>

# Nestor Agent

<p align="center">
  <a href="docs/README.md"><img alt="Tài liệu" src="https://img.shields.io/badge/DOCS-T%C3%80I_LI%E1%BB%86U-f4c430?style=for-the-badge"></a>
  <a href="docs/screenshots.md#tiếng-việt"><img alt="Ảnh chụp màn hình" src="https://img.shields.io/badge/GALLERY-%E1%BA%A2NH_CH%E1%BB%A4P-5457de?style=for-the-badge"></a>
  <a href="LICENSE"><img alt="Giấy phép: AGPL-3.0-or-later" src="https://img.shields.io/badge/LICENSE-AGPL--3.0--OR--LATER-4d8a16?style=for-the-badge"></a>
  <br>
  <a href="README.md"><img alt="English" src="https://img.shields.io/badge/LANG-ENGLISH-7c3aed?style=for-the-badge"></a>
</p>

Nestor Agent là trợ lý AI cá nhân mã nguồn mở chạy trên máy của bạn. Bạn có thể trò chuyện trong terminal hoặc trình duyệt, hỏi đáp về tài liệu và giao việc cho gateway chạy nền. Nestor lưu hội thoại, tệp workspace và bộ nhớ ngay trên máy. Bạn có thể chọn mô hình cục bộ hoặc nhà cung cấp đám mây.

## Nestor làm được gì?

| Tính năng | Cách sử dụng |
|---|---|
| **Chọn mô hình theo nhu cầu** | Chạy Ollama hoặc máy chủ cục bộ tương thích OpenAI, hoặc cấu hình Gemini, Claude, OpenAI, OpenRouter và các nhà cung cấp khác. Có thể đặt nhà cung cấp dự phòng. |
| **Terminal, trình duyệt và kênh chat** | Dùng CLI với phản hồi theo thời gian thực và lệnh gạch chéo, mở giao diện web có bảng workspace, hoặc kết nối Telegram hay Zalo OA qua gateway. |
| **Hỏi đáp trên tài liệu** | Lập chỉ mục PDF, Word, bảng tính, slide, Markdown và văn bản. Tìm trong một danh mục hoặc toàn bộ thư viện, rồi bấm trích dẫn để mở đoạn nguồn. OCR hỗ trợ PDF scan khi có Tesseract. |
| **Sổ tay và tệp văn phòng** | Chỉnh sửa ghi chú theo khối với bảng AI. Tạo tệp Word, Excel có công thức và PowerPoint. Trợ lý chuyên trách hỗ trợ soạn văn bản hành chính tiếng Việt. |
| **Giao việc nền và tự động hóa** | Giao thẻ Kanban cho agent, theo dõi tác vụ dài, lên lịch công việc định kỳ và dùng Heartbeat để kiểm tra việc cần chú ý. |
| **Bộ nhớ, kỹ năng và công cụ** | Dùng lại bộ nhớ Markdown và tìm trong hội thoại cũ. Cài kỹ năng dạng `SKILL.md` hoặc kết nối máy chủ MCP để thêm công cụ. |
| **Tích hợp với ứng dụng khác** | Gọi Nestor qua `POST /v1/run` bằng API token hoặc dùng công cụ `agent_run` từ một MCP client. |

## Cài nhanh

### Từ mã nguồn

Cần Python 3.11 trở lên. Nếu muốn build giao diện web, cần thêm Node.js 20 trở lên.

```bash
git clone https://github.com/tranvanhuy-hichan/ai-nestor-agent.git
cd ai-nestor-agent
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e app/backend
nestor onboard
```

Để dùng giao diện web, build frontend từ thư mục gốc của repo.

```bash
(cd app/frontend && npm install && npm run build)
nestor start
nestor open
```

### Docker

```bash
docker compose up -d --build
```

Mở giao diện web tại `http://127.0.0.1:8787`. Docker Compose lưu dữ liệu ở `./user-data`. Xem [hướng dẫn cài đặt](docs/huong-dan-su-dung.md#2-cài-đặt-và-chạy-lần-đầu) để biết thêm về gói desktop và cách thiết lập.

## Bắt đầu sử dụng

```bash
nestor                              # Trò chuyện trong terminal
nestor run "Tóm tắt tệp này"          # Chạy một tác vụ rồi thoát
nestor onboard                      # Thiết lập model, workspace và tích hợp
nestor status                       # Xem gateway và cấu hình hiện tại
nestor skills list                  # Xem danh sách kỹ năng
nestor logs -f                      # Theo dõi log gateway
nestor doctor                       # Chẩn đoán lỗi thiết lập
```

`nestor` và `nestor run` chạy trực tiếp trong terminal. Giao diện web và kênh chat cần gateway. Nếu muốn tự khởi động cùng máy, xem `nestor service install` trong [tài liệu CLI](docs/cli.md). CLI mặc định dùng tiếng Anh. Dùng `--lang vi` hoặc `NESTOR_LANG=vi` để chuyển sang tiếng Việt.

## Tài liệu

| Tài liệu | Nội dung |
|---|---|
| [Hướng dẫn sử dụng](docs/huong-dan-su-dung.md) | Cài đặt, mô hình, hội thoại, tài liệu, tự động hóa và xử lý sự cố |
| [Tài liệu CLI](docs/cli.md) | Lệnh, tùy chọn, biến môi trường và ví dụ |
| [API và trợ lý chuyên trách](docs/api-assistants.md) | Gọi trợ lý từ ứng dụng khác |
| [Kiến trúc](docs/kien-truc.md) | Gateway, vòng lặp agent, quyền công cụ và lưu trữ |
| [Ảnh chụp màn hình](docs/screenshots.md#tiếng-việt) | Giao diện web, trích dẫn tài liệu, sổ tay và terminal |

## Dữ liệu và bảo mật

Nestor mặc định lưu dữ liệu trong `user-data/`. Dùng `NESTOR_HOME` để chọn nơi lưu khác. Gateway mặc định chỉ lắng nghe trên localhost. Hãy xem qua kỹ năng tải về và máy chủ MCP trước khi bật, đồng thời giữ bước xác nhận cho các hành động bạn muốn kiểm soát. Dùng `nestor backup` trước khi chuyển workspace. Xem [chính sách bảo mật](SECURITY.md) để báo cáo lỗ hổng.

## Đóng góp

Bạn có thể báo lỗi hoặc đóng góp bản dịch, tài liệu, kỹ năng và mã nguồn. Xem [hướng dẫn đóng góp](CONTRIBUTING.md) và [quy tắc ứng xử](CODE_OF_CONDUCT.md).

## Giấy phép

GNU AGPL-3.0-or-later. Xem [LICENSE](LICENSE).
