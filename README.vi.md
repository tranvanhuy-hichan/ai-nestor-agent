<p align="center"><img src="docs/assets/nestor-logo.png" alt="Nestor" width="320"></p>

# Nestor Agent

<p align="center">
  <b>🇻🇳 Tiếng Việt</b> · <a href="README.md">🇬🇧 English</a>
</p>

<p align="center">
  <a href="LICENSE"><img alt="License: AGPL-3.0-or-later" src="https://img.shields.io/badge/license-AGPL--3.0--or--later-blue"></a>
  <img alt="Python 3.11+" src="https://img.shields.io/badge/python-3.11%2B-3776AB">
  <img alt="PRs welcome" src="https://img.shields.io/badge/PRs-welcome-brightgreen">
</p>

Trợ lý AI cá nhân **mã nguồn mở**, chạy trên máy bạn, dữ liệu nằm ở máy bạn: gateway chạy nền, giao diện web, **CLI `nestor`**, skill dạng `SKILL.md`, bộ nhớ bằng markdown, tool, MCP, Telegram và automations.

## Ảnh chụp màn hình

<p align="center"><img src="docs/assets/screenshots/vi/11-documents-category.png" alt="Tài liệu: mỗi danh mục có file riêng và khung chat chỉ trả lời từ các file đó, kèm trích dẫn nguồn" width="880"><br><sub><b>Tài liệu kiểu NotebookLM: mỗi danh mục có file riêng và khung chat chỉ trả lời từ các file đó, kèm trích dẫn bấm xem được</b></sub></p>

<table>
  <tr>
    <td width="50%"><img src="docs/assets/screenshots/vi/01-home.png" alt="Trang chủ"><br><sub><b>Trang chủ: việc gần đây, thông báo, lịch chạy sắp tới</b></sub></td>
    <td width="50%"><img src="docs/assets/screenshots/vi/02-chat.png" alt="Trò chuyện"><br><sub><b>Trò chuyện: câu trả lời Markdown, bảng, lệnh gọi công cụ hiện ngay trong chat</b></sub></td>
  </tr>
  <tr>
    <td width="50%"><img src="docs/assets/screenshots/vi/05-kanban.png" alt="Bảng Kanban"><br><sub><b>Kanban: giao việc cho thẻ và xem thẻ chuyển sang Đã xong</b></sub></td>
    <td width="50%"><img src="docs/assets/screenshots/vi/06-automations.png" alt="Việc theo lịch"><br><sub><b>Tự động hóa: việc theo lịch cron, Heartbeat, các mẫu có sẵn</b></sub></td>
  </tr>
  <tr>
    <td width="50%"><img src="docs/assets/screenshots/vi/03-tools.png" alt="Công cụ"><br><sub><b>Công cụ: quy trình có hướng dẫn cho công việc văn phòng</b></sub></td>
    <td width="50%"><img src="docs/assets/screenshots/vi/04-tasks.png" alt="Tác vụ"><br><sub><b>Tác vụ: giao việc dài cho agent rồi để nó chạy</b></sub></td>
  </tr>
  <tr>
    <td width="50%"><img src="docs/assets/screenshots/vi/07-skills.png" alt="Kỹ năng"><br><sub><b>Kỹ năng: gói SKILL.md bật tắt tùy ý</b></sub></td>
    <td width="50%"><img src="docs/assets/screenshots/vi/12-ai-models.png" alt="Mô hình AI"><br><sub><b>Mô hình AI: chạy cục bộ (Ollama) hoặc đám mây</b></sub></td>
  </tr>
</table>

### Sổ tay kiểu Notion

<table>
  <tr>
    <td width="50%"><img src="docs/assets/screenshots/vi/08-notebook-editor.png" alt="Trình soạn thảo khối của Sổ tay với callout, danh sách việc, toggle, khối mã và bảng"><br><sub><b>Soạn thảo theo khối: callout, danh sách việc, toggle, mã có tô màu, bảng, trang con</b></sub></td>
    <td width="50%"><img src="docs/assets/screenshots/vi/09-notebook-ai.png" alt="Sổ tay với khung chat AI"><br><sub><b>Khung AI: hỏi đáp hoặc để agent sửa thẳng vào ghi chú</b></sub></td>
  </tr>
  <tr>
    <td colspan="2" align="center"><img src="docs/assets/screenshots/vi/10-notebook-slash.png" alt="Menu gõ dấu gạch chéo để chèn khối" width="440"><br><sub><b>Gõ <code>/</code> để chèn một khối</b></sub></td>
  </tr>
</table>

### Terminal

<p align="center"><img src="docs/assets/screenshots/vi/13-cli-chat.png" alt="Giao diện CLI tương tác nestor với banner ASCII cyberpunk" width="880"><br><sub><b>Giao diện CLI tương tác (<code>nestor</code>) với banner ASCII và thẻ trạng thái thời gian thực</b></sub></p>

<table>
  <tr>
    <td width="50%"><img src="docs/assets/screenshots/vi/14-cli-status.png" alt="nestor status"><br><sub><b><code>nestor status</code></b></sub></td>
    <td width="50%"><img src="docs/assets/screenshots/vi/15-cli-help.png" alt="nestor --help"><br><sub><b><code>nestor --help</code>: toàn bộ lệnh trong một màn hình</b></sub></td>
  </tr>
</table>

> Ảnh chụp từ một không gian làm việc demo sạch với dữ liệu mẫu, không phải dữ liệu người dùng thật.

## Tính năng

- **Model**: Ollama và server local (LM Studio, vLLM), Gemini, Claude, OpenAI, OpenRouter, DeepSeek (DeepSeek-R1, V3), Mistral, xAI, Groq, Cerebras, Together, Fireworks, Qwen và mọi API tương thích OpenAI. Có fallback, tự thử lại khi lỗi 429/503, ước tính chi phí. Trình duyệt và chọn mô hình local trực quan.
- **Chat**: panel Workspace bên phải (Files, Terminal, Hoạt động), mọi lần gọi tool/MCP hiện ngay trong chat, hiển thị khối "suy nghĩ chuyên sâu" (Deep Thinking / `<think>`) tự động thu gọn/mở rộng, xem trước trực tiếp (Live Preview) cho file HTML/SVG do Agent tạo, đính kèm file/ảnh, nhập bằng giọng nói, sửa và tạo lại tin nhắn, lệnh `/skill`, `@dịch vụ`. Mỗi phiên có thư mục làm việc riêng (`user-data/workspace/sessions/<id>/`).
- **Kho tài liệu & RAG (Knowledge Base)**: nạp và lập chỉ mục đa định dạng (PDF, Word `.docx`, Excel `.xlsx`, `.csv`, PowerPoint `.pptx`, Markdown, Text) với thanh tiến trình nạp trực quan. Bật chế độ "Hỏi từ tài liệu" ngay trên thanh chat để Agent đối chiếu tri thức và trả lời kèm trích dẫn nguồn gốc tương tác `[1]`, `[2]` (bấm vào xem ngay câu trích và số trang gốc).
- **Danh mục tài liệu (kiểu NotebookLM)**: nhóm file theo danh mục. Mở một danh mục sẽ thấy danh sách file bên trái và khung chat bên phải **chỉ trả lời từ tài liệu của danh mục đó**, kèm trích dẫn nguồn bấm xem được. Menu ba chấm ở mỗi file mở file gốc ở tab mới, kéo thanh phân cách để đổi độ rộng khung chat, còn nút **Hỏi toàn bộ kho** vẫn tìm trong mọi tài liệu. File đã thêm từ trước được tự gom vào một danh mục mặc định.
- **Sổ tay (kiểu Notion)**: trình soạn thảo theo khối với menu `/` để chèn tiêu đề, danh sách đầu dòng/đánh số/việc cần làm, toggle, callout, khối mã có tô màu cú pháp, bảng, ảnh và trang con; chế độ xem toàn chiều rộng cho từng trang; xuất Markdown một chạm. Khung AI bên phải đọc được ghi chú, sửa thẳng vào đó hoặc tạo trang con có liên kết. Ghi chú lưu dạng JSON theo khối ở `workspace/pages/<id>.json`; ghi chú của các phiên bản trước (`.md`) vẫn nằm nguyên trên đĩa nhưng không tự động chuyển đổi.
- **Kanban & tác vụ**: lên kế hoạch bằng thẻ, kéo-thả sắp xếp, bấm Giao việc để chạy thẻ ở nền; thẻ chuyển qua Việc cần làm, Đang làm, Chặn/Lỗi và Đã xong theo tiến trình chạy. Việc dài có thể giao ở trang Tác vụ và theo dõi tại đó.
- **Thanh công cụ tinh gọn & Tùy biến sâu**:
  - Chọn model AI trực tiếp với nhãn chi tiết.
  - Nút **Mức suy luận & Tham số**: chọn mức suy nghĩ (`Tự động`, `Suy nghĩ chuyên sâu`, `Thấp`, `Vừa`, `Cao`), thanh trượt **Nhiệt độ (Temperature)** (0.0 - 1.5) và **Độ dài tối đa (Max Tokens)** (1k - 8k).
  - Nút **Quyền hạn & Hạn mức**: chọn quyền thực thi (`Mặc định`, `An toàn`, `Toàn quyền`) và xem biểu đồ hạn mức token (Quota 5h / 7 ngày).
- **Quản lý hội thoại thông minh**: tự động đặt tên hội thoại ngắn gọn (Auto-naming) sau câu trả lời đầu tiên, ghim các phiên quan trọng lên đầu danh sách (Pin), sidebar mở rộng tự xuống dòng (`line-clamp-2`) không bị cắt tiêu đề, tìm kiếm toàn văn lịch sử chat.
- **Skills**: đọc định dạng skill `SKILL.md` (tương thích [ClawHub](https://clawhub.ai)), duyệt, cài và cập nhật từ ClawHub.
- **MCP client**: nối MCP server của bạn (stdio, HTTP, SSE); tool xuất hiện dưới dạng `tênserver__têntool`.
- **Cho app khác gọi agent**: `POST /v1/run` với API token, hoặc MCP server (`agent_run`) dùng được trong Claude Code, Cursor...
- **Trợ lý văn phòng (kiểu COffice AI)**: tạo file Word/Excel (công thức sống)/PowerPoint thật, soạn và **rà thể thức văn bản hành chính theo NĐ 30/2020**; 10 **trợ lý chuyên trách** (văn thư, văn bản Đảng HD 05, tổng hợp báo cáo, thư ký, kế toán, nhân sự, kinh doanh, dự án, pháp chế, IT) và trợ lý tự tạo; kênh **Zalo OA** (nhắn việc, nhận kết quả, ghép đôi như Telegram); automation **Tóm tắt buổi sáng**; nút **đúc kết hội thoại thành Skill/Rule**; **tổ công tác** nhiều agent chạy song song có bảng ghi chép chung; agent **tự viết và chạy script** xử lý hàng loạt rồi lưu thành kỹ năng.
- **Chủ động**: Automations (cron), Heartbeat (agent tự kiểm tra `HEARTBEAT.md` và nhắn khi cần), Hộp thư thông báo, kênh **Telegram** (nút phê duyệt ngay trong chat, nhận/gửi file).
- **Bộ nhớ**: `MEMORY.md`, tìm kiếm toàn văn mọi hội thoại cũ (`memory_search`), tự tóm tắt hội thoại dài.
- **Song ngữ Việt/Anh**: đổi ngôn ngữ ở đầu thanh bên (và CLI theo `--lang`). Thêm chuỗi mới: bọc `t('câu tiếng Việt')` rồi thêm bản Anh vào `app/frontend/src/i18n/en/`; `npm run i18n:check` bắt chuỗi sót, thiếu bản dịch hoặc dịch xung đột.
- **An toàn mặc định**: lệnh shell, file ngoài thư mục phiên và tool MCP hỏi xác nhận; tùy chọn sandbox Docker (không mạng); mật khẩu đăng nhập tùy chọn; nhật ký mọi lần gọi tool; chỉ nhận kết nối từ localhost; token API chỉ lưu bản băm.

## Giao diện nâng cao

- **Chat** có bộ chọn hồ sơ, ngăn **Quyền công cụ** và cảnh báo khi lượt gọi gần nhất dùng ít nhất 80% cửa sổ ngữ cảnh. Có thể tóm tắt các lượt cũ hoặc xem lại điểm nhấn trước khi lưu vào bộ nhớ.
- **Hồ sơ trợ lý** có hướng dẫn, thứ tự mô hình, kỹ năng, danh sách công cụ và bộ nhớ riêng. Biến môi trường của hồ sơ tham chiếu tên biến đã đặt trên máy chủ theo dạng `TEN_DICH=TEN_NGUON`.
- **Tự động hóa** có mẫu báo cáo tuần NĐ 30, tóm tắt YouTube Live, rà soát bộ nhớ và theo dõi GitHub PR. **Tích hợp → Kênh chat** duyệt quyền Telegram và Zalo OA. Mã ghép đôi tạo yêu cầu để người quản trị duyệt.
- **Sức khỏe hệ thống** hiển thị tài nguyên, trạng thái Gateway và log trực tiếp. Có thể khởi động lại từ web khi Gateway chạy nền bằng `nestor start` hoặc bằng dịch vụ systemd người dùng `nestor.service`. **Cài đặt** lưu bảng màu và phông chữ theo trình duyệt.

Để mở **Chat → Terminal** trên POSIX, đặt mật khẩu Nestor rồi khởi động Gateway với biến môi trường `NESTOR_WEB_TERMINAL=1`. Terminal chạy với quyền tài khoản hệ điều hành của Gateway.

## Tài liệu

- [Hướng dẫn sử dụng](docs/huong-dan-su-dung.md): dành cho mọi người dùng
- [Tài liệu dòng lệnh `nestor`](docs/cli.md)
- [Kiến trúc hệ thống](docs/kien-truc.md): dành cho lập trình viên

## Cài đặt

Cần Python 3.11+ (và Node 20+ nếu muốn tự build giao diện).

```bash
git clone https://github.com/tranvanhuy-hichan/nestor-agent.git && cd nestor-agent
python3 -m venv .venv && .venv/bin/pip install -e app/backend
(cd app/frontend && npm install && npm run build)     # giao diện web
.venv/bin/nestor onboard                           # trình hướng dẫn: model, an toàn, Telegram, khởi động
```

Thêm `.venv/bin` vào `PATH` (hoặc `source .venv/bin/activate`) để gõ ngắn `nestor ...`.

## CLI `nestor`

| Lệnh | Việc |
|---|---|
| `nestor onboard` | Cài đặt lần đầu: menu chọn bằng **↑/↓, Space (tick), Enter**, nút Có/Không đổi bằng ←/→. Khi không có terminal thật (pipe, CI, Windows) tự dùng kiểu gõ số; `--non-interactive` + cờ để tự động hóa |
| `nestor start` / `stop` / `restart` / `status` | Quản lý server nền (`start -f` chạy foreground, `--host 0.0.0.0` để mở cho máy khác) |
| `nestor logs -f` | Xem log |
| `nestor open` | Mở giao diện web |
| `nestor doctor` | Chẩn đoán (`--fix` tự sửa việc an toàn, `--offline`, `--json`) |
| `nestor chat` | Trò chuyện ngay trong terminal (hỏi `y/N` khi cần phê duyệt; `/help` xem lệnh) |
| `nestor run "việc cần làm"` | Chạy một lần rồi thoát: `--json`, `--exec-policy deny\|allow\|allowlist`, `--allow "git status"`, `--ask`, `--permission readonly`, `-` để đọc stdin |
| `nestor token create\|list\|revoke` | API token cho `/v1/run` và MCP server |
| `nestor skills list\|search\|install\|remove\|update` | Skill từ ClawHub |
| `nestor service install\|uninstall\|start\|stop\|status` | Chạy cùng máy (systemd trên Linux, launchd trên macOS; `install --dry-run` để xem trước) |
| `nestor backup` / `restore` | Sao lưu và khôi phục cấu hình, cơ sở dữ liệu, workspace. `--encrypt` mã hóa bằng mật khẩu, `--include-key` kèm khóa chủ, `restore --force` tự sao lưu bản hiện tại trước |
| `nestor secrets status\|encrypt\|decrypt\|keychain\|file\|rotate` | Quản lý việc mã hóa khóa bí mật trong `config.json` |
| `nestor config path\|show` | Xem cấu hình (API key được che) |

`chat` và `run` chạy agent ngay trong tiến trình (không cần server đang chạy) và dùng chung cấu hình, skill, MCP, hội thoại với giao diện web. Đổi ngôn ngữ CLI: `--lang vi|en` hoặc `NESTOR_LANG`.

Biến môi trường: `NESTOR_HOME` (thư mục dữ liệu), `NESTOR_PORT`, `NESTOR_HOST`, `NESTOR_CONFIG`, `NESTOR_ALLOWED_HOSTS`, `NESTOR_TOKEN`/`NESTOR_URL` (MCP server). Tên cũ `AGENT_*` vẫn được nhận.

`./run.sh` vẫn dùng được như lớp bọc mỏng quanh `nestor`.

## Docker, service, test

```bash
docker compose up -d --build         # mở http://127.0.0.1:8787 (dữ liệu cá nhân ở ./user-data)
nestor service install                # chạy cùng máy, không cần Docker
cd app/backend && pip install -e ".[dev]" && python -m pytest -q
```

Tìm Ollama trên máy chủ từ trong container: đặt Base URL là `http://host.docker.internal:11434/v1`.

## Đóng góp

Nestor là dự án mã nguồn mở và rất hoan nghênh đóng góp: báo lỗi, đề xuất tính năng, cải thiện tài liệu, bản dịch, skill mới, code.

1. Mở [issue](https://github.com/tranvanhuy-hichan/nestor-agent/issues) để báo lỗi hoặc bàn ý tưởng trước khi làm việc lớn.
2. Fork repo, tạo nhánh từ `main` (ví dụ `feat/ten-tinh-nang`).
3. Chạy kiểm tra trước khi gửi: `cd app/backend && python -m pytest -q` và `cd app/frontend && npm run i18n:check`.
4. Gửi Pull Request mô tả rõ thay đổi và lý do. Commit theo kiểu `feat:`, `fix:`, `docs:`...
5. Thêm ngôn ngữ mới hoặc sửa bản dịch: xem mục *Song ngữ* ở phần Tính năng.

Báo lỗ hổng bảo mật: vui lòng không đăng công khai, hãy liên hệ riêng với tác giả qua GitHub.

## Giấy phép

Nestor Agent là phần mềm tự do theo giấy phép **GNU AGPL-3.0-or-later** (xem [LICENSE](LICENSE)). Nếu bạn sửa đổi và cung cấp nó như một dịch vụ qua mạng, bạn phải cung cấp mã nguồn bản sửa đổi cho người dùng dịch vụ đó.

Copyright (C) 2026 tranvanhuy-hichan

## Cấu trúc thư mục

Dự án tách làm hai phần để không bao giờ nhầm lẫn mã nguồn với dữ liệu của bạn:

```
nestor-agent/
├── app/                  # MÃ NGUỒN CỐ ĐỊNH: có thể xóa/cài lại bất cứ lúc nào mà không mất gì của bạn
│   ├── backend/nestor/
│   │   ├── api/          # router FastAPI: chat, skills, providers, tích hợp, API ngoài (/v1)
│   │   ├── services/     # agent loop, providers, tools, skills, MCP, Telegram, scheduler, trình duyệt…
│   │   ├── core/         # cấu hình, SQLite, đường dẫn
│   │   └── cli/          # lệnh `nestor` (start, doctor, onboard, chat, run, tasks, memory…)
│   ├── frontend/src/     # React + TypeScript + Tailwind (features/ theo từng trang, i18n/)
│   ├── templates/workspace/   # SOUL.md và skill mẫu, dùng để tạo workspace lần đầu
│   ├── deploy/           # file systemd mẫu
│   └── examples/         # MCP server mẫu để thử tích hợp
├── user-data/            # DỮ LIỆU CÁ NHÂN CỦA BẠN: đừng xóa, hãy sao lưu (`nestor backup`)
│   ├── config.json       # cấu hình (API key đã mã hóa)
│   ├── data/             # cơ sở dữ liệu, khóa chủ (master.key), log
│   ├── workspace/        # SOUL.md, USER.md, MEMORY.md, skills/, sessions/ (tính cách, bộ nhớ, file của agent)
│   └── backups/          # các bản sao lưu
├── Dockerfile, docker-compose.yml, run.sh, .github/, LICENSE, README.md
```

Muốn để dữ liệu ở nơi khác (ổ khác, thư mục được đồng bộ…): đặt biến môi trường `NESTOR_HOME=/duong/dan`. Nếu bạn cài từ phiên bản cũ (dữ liệu nằm ngay ở thư mục gốc), Nestor vẫn dùng chỗ đó cho tới khi bạn chuyển `config.json`, `data/`, `workspace/`, `backups/` vào `user-data/`.

## Lưu ý bảo mật

- Skill tải từ internet chỉ là hướng dẫn, nhưng có thể bảo agent chạy lệnh. Đọc `SKILL.md` trước khi cài và giữ xác nhận lệnh shell luôn bật.
- MCP server stdio chạy lệnh bạn khai báo với quyền của chính bạn. Chỉ thêm server bạn tin tưởng.
- `user-data/config.json` (cả thư mục `user-data/` đã nằm trong `.gitignore`). Mọi khóa bí mật trong đó (API key, token Telegram, biến môi trường/header MCP, khóa skill) được **mã hóa** bằng khóa chủ lấy từ `NESTOR_MASTER_KEY`, keychain hệ điều hành (`pip install keyring` rồi `nestor secrets keychain`) hoặc `user-data/data/master.key` (quyền 600). Việc này bảo vệ khi file config bị lộ riêng lẻ (gửi kèm báo lỗi, đẩy nhầm lên git, sao lưu rời khóa chủ); **không** bảo vệ khi kẻ tấn công có cả hai file hoặc đang chạy trên máy của bạn. Hãy sao lưu khóa chủ (`nestor backup --include-key --encrypt`): mất nó thì không giải mã lại được. `nestor doctor` kiểm tra tình trạng này.
