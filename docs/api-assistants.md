# API: trợ lý văn phòng (cho giao diện)

Mọi đường dẫn có tiền tố `/api`. Lỗi nghiệp vụ trả `400 {"detail": "..."}`.

## Trợ lý chuyên trách
- `GET /assistants` → `[{id, name, icon (tên lucide), group: "co-quan"|"doanh-nghiep", description, prompt, starters: string[3], skills: string[], builtin: bool}]`
  id dựng sẵn: van-thu-nd30, van-ban-dang-hd05, tong-hop-bao-cao, thu-ky, ke-toan, nhan-su, kinh-doanh-marketing, quan-ly-du-an, phap-che, it.
- `POST /assistants/{id}` (tạo), `PUT /assistants/{id}` (sửa), body `{name, prompt, icon?="bot", group?, description?, starters?: string[], skills?: string[]}` → trợ lý. id: `[a-z0-9-]`. Không sửa/xóa được trợ lý dựng sẵn (400).
- `DELETE /assistants/{id}` → `{ok:true}`
- `POST /chat` nhận thêm `assistant?: string` (id) — chỉ áp dụng cho lượt đó, giao diện nên gửi lại mỗi lượt của phiên.

## Zalo OA
- `GET /channels` → có thêm `zalo`; `GET /channels/zalo` → `{running, error, oa, enabled, oa_id, app_id, allowed_users: string[], has_app_secret, has_access_token, has_refresh_token, has_webhook_secret, webhook_path}`
- `PUT /channels/zalo` body `{enabled, oa_id, app_id, app_secret, access_token, refresh_token, webhook_secret}` (chuỗi rỗng hoặc `"***"` = giữ giá trị cũ). Bật cần access/refresh token và `webhook_secret`. Trả như GET.
- `POST /channels/zalo/pair-code` → `{code, expires_in: 600}`; người dùng nhắn Zalo `/pair <mã>`.
- `POST /channels/zalo/remove-user` `{user_id: string}`
- `POST /channels/zalo/webhook` (Zalo gọi; dán URL công khai `https://<tunnel>/api/channels/zalo/webhook?secret=<webhook_secret>` vào Zalo OA).

## Tóm tắt buổi sáng
- `POST /automations/templates/morning-brief` body `{time?: "HH:MM"="07:30", provider?}` → `{id, name, schedule (cron), updated: bool}`. Idempotent (tên "Tóm tắt buổi sáng"); hiện trong `GET /automations`.

## Đúc kết Skill/Rule
- `POST /sessions/{id}/distill` body `{kind: "skill"|"rule", name?, provider?}` →
  skill: `{kind:"skill", name, description, content (SKILL.md)}`; rule: `{kind:"rule", id, text}`.
- `GET /rules` → `[{id: number, text}]`; `POST /rules {text}`; `DELETE /rules/{id}` (id = vị trí, 404 nếu không có).

## Tổ công tác
- Công cụ `team_run(goal, members)` (agent tự gọi). Khi bắt đầu, luồng chat phát sự kiện `{type:"team", id, goal, members:[{role, task}]}`.
- `GET /teams` → `[{id, goal, status, created, members: number}]`
- `GET /teams/{id}/status` → `{id, goal, status: "running"|"done"|"partial", created, session_id, notes: {key: {text, author, ts}}, members: [{role, task, status: "queued"|"running"|"done"|"failed", job_id, result, error}], review: {status: "pending"|"running"|"done"|"failed", result}, result}` — giao diện nên poll 1-2 giây/lần khi `status == "running"`. 404 nếu không có.

## Công cụ mới cho agent
`create_docx`, `create_xlsx`, `create_pptx`, `vanban_write_docx`, `review_vn_document(path)`, `run_script(name, code, timeout?)` (cần phê duyệt `exec`), `save_script_as_skill(name, description, script_path)`, `team_run`, `team_note_write`, `team_note_read`.


## Trợ lý "thật": kỹ năng, cổng chất lượng, allowlist, lưu theo phiên

Định nghĩa trợ lý dựng sẵn nằm ở `argus/assistant_defs/gov_biz.py` và `edu_personal.py` (mỗi file có `DEFS`), skill đi kèm ở `argus/bundled_skills/<slug>/SKILL.md`.
Trợ lý cũ viết thẳng trong `services/assistants.py` (`LEGACY`) chỉ còn là dự phòng: id trùng thì bản trong `assistant_defs` thắng.

Một định nghĩa: `{id, name, icon, group, description, prompt, starters[>=3], skills[], tools|null, done_criteria[>=3], deliverables[]}`.
`GET /api/assistants` trả thêm `skills`, `tools`, `done_criteria`, `deliverables`. `group` thuộc `co-quan | doanh-nghiep | hoc-sinh | giao-vien | sinh-vien | ca-nhan`.

- **Skill được nhúng nguyên văn**: `prompt_for(id)` chèn toàn bộ SKILL.md của các skill trong `skills` (tối đa 12000 ký tự) vào system prompt, không chờ model tự gọi `skills_read`. Skill đi kèm chỉ đọc; skill cùng tên trong `workspace/skills` thay thế bản đi kèm; chúng không xuất hiện trong danh sách skill chung của mọi cuộc trò chuyện (chỉ trợ lý nạp).
- **Cổng chất lượng**: `prompt_for` luôn thêm khối bắt buộc: tự kiểm từng `done_criteria`, sửa nếu chưa đạt, tạo đúng file `deliverables` bằng tool, rồi kết thúc bằng danh sách ✓/✗ và danh sách file. Chỉ hỏi lại người dùng khi thiếu thông tin thiết yếu.
- **Allowlist tool**: `tools` khác `null` thì chỉ các tool đó (cộng `ask_user`, `plan_*`, `remember`, `memory_search`, `skills_read`, `delegate`) được đề xuất cho model và được phép gọi; tool ngoài danh sách bị từ chối ("không có tool …"), kể cả tool MCP. Cũng áp dụng cho danh sách khôi phục của chế độ Kế hoạch.
- **Lưu theo phiên**: cột `sessions.assistant` (tự thêm bằng migration). `POST /api/chat` với `assistant: "<id>"` lưu lại cho phiên; bỏ trống `assistant` thì dùng bản đã lưu; `assistant: ""` bỏ chọn. `GET /api/sessions/{sid}` và `GET /api/sessions` trả `assistant`. `PUT /api/sessions/{sid}/assistant {assistant}` đặt/bỏ chọn (id lạ: 400, phiên lạ: 404).
- **Trợ lý tự tạo** (POST/PUT) nhận thêm `tools`, `done_criteria`, `deliverables`.

**Giới hạn trung thực:** test trong `tests/test_assistant_contract.py` dùng provider giả theo kịch bản, chỉ chứng minh dây nối (skill và cổng chất lượng nằm trong prompt, allowlist được ép, lưu theo phiên, tool tạo file chạy được, định nghĩa đủ tiêu chí hợp đồng). Chúng không đo được chất lượng câu trả lời của mô hình thật.
