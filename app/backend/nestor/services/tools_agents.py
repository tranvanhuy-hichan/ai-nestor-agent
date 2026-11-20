"""Tool giao viec: delegate (agent con), task_start/task_status/task_cancel (viec chay nen)."""
from ..core import config as cfgmod
from . import jobs
from .tools import ToolContext, tool


def _result_text(job: dict, label: str) -> str:
    head = f"{label} (job {job['id']}, {job['steps']} bước, {job['status']})"
    if job["status"] == "done":
        return f"{head}:\n{job['result'] or '(không có kết quả)'}"
    return f"{head} KHÔNG thành công: {job['error'] or 'bị dừng'}" + (f"\nKết quả dở dang: {job['result']}" if job["result"] else "")


@tool("delegate", "Giao một việc cho agent con chuyên trách rồi nhận kết quả (chạy xong mới trả về). Dùng khi việc cần chuyên môn riêng hoặc muốn làm song song: gọi nhiều delegate trong cùng một lượt để chạy đồng thời. Vai trò có sẵn: researcher, coder, reviewer, general.",
      {"role": ("string", "vai trò: researcher, coder, reviewer hoặc general"), "task": ("string", "mô tả đầy đủ việc cần làm và kết quả mong muốn (agent con không thấy hội thoại này)")})
def delegate(ctx: ToolContext, role, task):
    if not task.strip():
        raise ValueError("thiếu mô tả việc cần giao")
    return _result_text(jobs.run_subagent(ctx, role.strip().lower() or "general", task.strip()), f"Agent con '{role}'")


@tool("task_start", "Bắt đầu một VIỆC CHẠY NỀN (có thể kéo dài nhiều phút, nhiều bước) rồi trả lời người dùng ngay. Khi xong sẽ có thông báo. Dùng cho việc lớn không cần chờ kết quả ngay.",
      {"goal": ("string", "mục tiêu đầy đủ, tự chứa mọi thông tin cần thiết"), "title": ("string", "tên ngắn của việc"), "role": ("string", "vai trò (tùy chọn): researcher, coder, reviewer, general")},
      required=["goal"])
def task_start(ctx: ToolContext, goal, title="", role="general"):
    cfg = cfgmod.load()
    if ctx.depth >= cfg.agents.max_depth:
        raise ValueError("agent con không được tạo việc nền")
    jid = jobs.start_background(goal.strip(), kind="task", title=title or goal[:60], role=(role or "general").lower(), parent_session=ctx.session_id, permission=ctx.permission, provider=ctx.provider)
    return f"Đã bắt đầu việc nền {jid} ({title or goal[:60]}). Chạy ngầm; dùng task_status {jid} để xem tiến độ. Người dùng sẽ nhận thông báo khi xong."


@tool("task_status", "Xem tiến độ một việc chạy nền (theo id) hoặc liệt kê các việc gần đây.", {"id": ("string", "id việc nền; bỏ trống để liệt kê")}, required=[])
def task_status(ctx: ToolContext, id=""):
    if id:
        job = jobs.get(id)
        if not job or job["assistant_scope"] != ctx.profile_id:
            return f"không có việc '{id}'"
        return f"{job['title']} [{job['status']}] {job['steps']}/{job['max_steps'] or '?'} bước" + (f"\nĐang: {job['progress']}" if job["progress"] else "") + (f"\nKết quả:\n{job['result']}" if job["result"] else "") + (f"\nLỗi: {job['error']}" if job["error"] else "")
    rows = jobs.list_jobs(kind="task", limit=10, scope=ctx.profile_id)
    return "\n".join(f"{j['id']}  [{j['status']}]  {j['title']}  ({j['steps']} bước)" for j in rows) or "chưa có việc nền nào"


@tool("task_cancel", "Hủy một việc chạy nền đang chạy.", {"id": ("string", "id việc nền")})
def task_cancel(ctx: ToolContext, id):
    job = jobs.get(id)
    return "đã yêu cầu hủy" if job and job["assistant_scope"] == ctx.profile_id and jobs.request_cancel(id) else f"không hủy được '{id}' (không tồn tại hoặc đã kết thúc)"


# ---------------------------------------------------------------- to cong tac
import json as _json  # noqa: E402
import threading as _threading  # noqa: E402

from . import teams  # noqa: E402

MAX_MEMBERS = 8


def _parse_members(members) -> list[dict]:
    if isinstance(members, str):
        try:
            members = _json.loads(members)
        except ValueError:
            members = [m for m in members.splitlines() if m.strip()]
    out = []
    for m in members or []:
        if isinstance(m, str):
            try:
                m = _json.loads(m)
            except ValueError:
                role, _, task = m.partition(":")
                m = {"role": role, "task": task}
        role, task = str(m.get("role") or "general").strip().lower(), str(m.get("task") or "").strip()
        if task:
            out.append({"role": role, "task": task})
    if not out:
        raise ValueError("cần ít nhất một thành viên có việc cụ thể: [{\"role\": \"researcher\", \"task\": \"...\"}]")
    if len(out) > MAX_MEMBERS:
        raise ValueError(f"tối đa {MAX_MEMBERS} thành viên")
    return out


@tool("team_run", "Lập TỔ CÔNG TÁC: chia một việc lớn cho nhiều thành viên chuyên trách chạy SONG SONG, dùng chung bảng ghi chép (team_note_write/team_note_read), rồi một người rà soát kiểm tra chéo và trả về kết quả tổng hợp. Dùng cho hồ sơ lớn, tổng hợp báo cáo nhiều đơn vị.",
      {"goal": ("string", "mục tiêu chung của cả tổ"), "members": ("string", "JSON mảng thành viên [{\"role\": \"researcher|coder|reviewer|general\", \"task\": \"việc cụ thể, tự chứa đủ thông tin\"}]")})
def team_run(ctx: ToolContext, goal, members):
    cfg = cfgmod.load()
    if ctx.depth >= cfg.agents.max_depth:
        raise ValueError("agent con không được lập tổ công tác")
    ms = _parse_members(members)
    team = teams.create(goal, ms, ctx.session_id)
    ctx.emit({"type": "team", "id": team["id"], "goal": goal, "members": [{"role": m["role"], "task": m["task"]} for m in ms]})
    head = (f"Bạn là thành viên của tổ công tác {team['id']} với mục tiêu chung: {goal}\n"
            f"Dùng team_note_write(team=\"{team['id']}\", key, text) để chia sẻ phát hiện/số liệu cho đồng đội và team_note_read(team=\"{team['id']}\") để đọc ghi chép của họ.\n\nViệc của bạn: ")

    def work(m: dict) -> None:
        m["status"] = "running"
        try:
            job = jobs.run_subagent(ctx, m["role"], head + m["task"])
            m["job_id"], m["result"] = job["id"], job["result"] or ""
            m["status"], m["error"] = ("done", "") if job["status"] == "done" else ("failed", job["error"] or "bị dừng")
        except Exception as e:  # noqa: BLE001 - mot thanh vien loi khong lam hong ca to
            m["status"], m["error"] = "failed", f"{type(e).__name__}: {e}"

    threads = [_threading.Thread(target=work, args=(m,), daemon=True) for m in team["members"]]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    parts = "\n\n".join(f"### {m['role']} ({m['status']}): {m['task'][:100]}\n{m['result'] or '(trống)'}{' [LỖI: ' + m['error'] + ']' if m['error'] else ''}" for m in team["members"])
    review = team["review"]
    try:
        review["status"] = "running"
        job = jobs.run_subagent(ctx, "reviewer", f"Kiểm tra chéo kết quả của tổ công tác. Mục tiêu: {goal}\nGhi chép chung:\n{teams.note_read(team['id'])}\n\nKết quả các thành viên:\n{parts}\n\n"
                                "Chỉ ra mâu thuẫn, số liệu vênh, phần còn thiếu; kết luận ngắn gọn.")
        review["result"], review["status"] = job["result"] or "", "done" if job["status"] == "done" else "failed"
    except Exception as e:  # noqa: BLE001
        review["status"], review["result"] = "failed", f"{type(e).__name__}: {e}"
    team["result"] = f"{parts}\n\n### Rà soát chéo ({review['status']})\n{review['result']}"
    team["status"] = "done" if all(m["status"] == "done" for m in team["members"]) else "partial"
    return f"Tổ công tác {team['id']} ({team['status']}):\n\n{team['result']}"


@tool("team_note_write", "Ghi vào bảng ghi chép chung của tổ công tác để đồng đội đọc được.",
      {"team": ("string", "id tổ công tác (có trong yêu cầu giao việc)"), "key": ("string", "tiêu đề ghi chép"), "text": ("string", "nội dung")})
def team_note_write(ctx: ToolContext, team, key, text):
    teams.note_write(team, key, text, author=f"depth{ctx.depth}")
    return "đã ghi"


@tool("team_note_read", "Đọc bảng ghi chép chung của tổ công tác (một mục hoặc tất cả).",
      {"team": ("string", "id tổ công tác"), "key": ("string", "tiêu đề; bỏ trống để đọc tất cả")}, required=["team"])
def team_note_read(ctx: ToolContext, team, key=""):
    return teams.note_read(team, key)
