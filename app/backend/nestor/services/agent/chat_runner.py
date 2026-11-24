"""Chay mot luot chat trong thread rieng va day su kien ra queue (cho SSE). Quan ly xin phep (approval)."""
import re
from contextlib import contextmanager
import threading
import uuid
from collections.abc import Iterator
from pathlib import Path

import time

from nestor.core import config as cfgmod
from nestor.core.db import db
from nestor.services import agent, sessions, workfiles
from nestor.services.system import work_runs

APPROVAL_TIMEOUT = 300
_approvals: dict[str, dict] = {}
_questions: dict[str, dict] = {}
QUESTION_TIMEOUT = 900


def _output_files(sid: str, events: list[dict]) -> list[str]:
    paths = [item["path"] for event in events if event["type"] == "turn_summary" for item in event["files"]]
    if not paths:
        return []
    root = workfiles.workdir_for(cfgmod.load(), sid).resolve()
    files = []
    for name in paths:
        path = (root / Path(name)).resolve()
        if root in path.parents and path.is_file():
            files.append(path.relative_to(root).as_posix())
    return list(dict.fromkeys(files))


def _auto_name_session(sid: str, user_text: str, provider: str | None) -> None:
    try:
        sess = sessions.get(sid)
        if not sess or sess.get("source") == "telegram":
            return
        msgs = sessions.messages(sid)
        if len(msgs) <= 2:
            from nestor.core import config as cfgmod
            from nestor.services.providers import make_provider
            cfg = cfgmod.load()
            pname = provider or cfg.default_provider
            pcfg = cfg.providers.get(pname)
            if not pcfg:
                return
            prompt_name = (
                f"Hãy tóm tắt yêu cầu sau thành một tiêu đề ngắn gọn từ 3 đến 6 từ tiếng Việt, "
                f"viết hoa chữ cái đầu câu, không dùng dấu ngoặc kép, không giải thích gì thêm:\n\"{user_text[:200]}\""
            )
            prov = make_provider(pcfg)
            res = ""
            for ev in prov.stream([{"role": "user", "content": prompt_name}], tools=[]):
                if ev.get("type") == "delta":
                    res += ev.get("text", "")
            clean = re.sub(r'["\'\n\r.]', '', res).strip()
            if clean and len(clean) <= 50 and not clean.lower().startswith("hãy"):
                sessions.rename(sid, clean)
    except Exception:
        pass


def answer_question(qid: str, text: str) -> bool:
    q = _questions.get(qid)
    if not q:
        return False
    q["answer"] = text
    q["event"].set()
    return True


def resolve_approval(aid: str, ok: bool) -> bool:
    a = _approvals.get(aid)
    if not a:
        return False
    a["ok"] = ok
    a["event"].set()
    return True


class Run:
    """Mot luot chay agent song doc lap voi ket noi HTTP: su kien duoc luu lai de client doi trang roi noi lai (attach) van xem tiep duoc."""

    def __init__(self, sid: str, text: str, attachments: list[str], base_count: int, document_ids: list[str] | None = None) -> None:
        self.id = uuid.uuid4().hex
        self.sid, self.events, self.done = sid, [], False
        self.user = {"text": text, "attachments": attachments}
        if document_ids:
            self.user["document_ids"] = document_ids
        self.base_count = base_count
        self.cond = threading.Condition()
        self.cancel = threading.Event()
        self.finished_at = 0.0

    def push(self, ev: dict) -> None:
        with self.cond:
            self.events.append(ev)
            if ev["type"] == "done":
                self.done, self.finished_at = True, time.time()
            self.cond.notify_all()

    def tail(self, start: int = 0) -> Iterator[dict]:
        i = start
        while True:
            with self.cond:
                if i >= len(self.events) and not self.done:
                    self.cond.wait(15)
                batch, i = self.events[i:], len(self.events)
                finished = self.done
            if batch:
                yield from batch
            elif not finished:
                yield {"type": "ping"}
            if finished:
                return


_runs: dict[str, Run] = {}
_runs_lock = threading.Lock()
_session_edits: set[str] = set()
KEEP_FINISHED = 120  # giu su kien cua luot da xong de client noi lai kip nhan ket qua


def _gc() -> None:
    now = time.time()
    for k, r in list(_runs.items()):
        if r.done and now - r.finished_at > KEEP_FINISHED:
            _runs.pop(k, None)


def state(sid: str) -> dict:
    """Trang thai cho client noi lai: dang chay khong, da co bao nhieu su kien (cursor), xin phep dang cho."""
    r = _runs.get(sid)
    pending = [{"id": k, "kind": a["kind"], "detail": a["detail"]} for k, a in _approvals.copy().items() if a.get("sid") == sid]
    questions = [{"id": k, "question": q["question"], "options": q["options"], **({"form": q["form"]} if q.get("form") else {})} for k, q in _questions.copy().items() if q.get("sid") == sid]
    return {"active": bool(r and not r.done), "cursor": len(r.events) if r else 0,
            "run_id": r.id if r else None, "base_count": r.base_count if r else 0,
            "user": r.user if r else None, "pending": pending, "questions": questions}


def active(sid: str) -> bool:
    r = _runs.get(sid)
    return bool(r and not r.done)



@contextmanager
def edit_idle_session(sid: str):
    with _runs_lock:
        editable = not active(sid) and sid not in _session_edits
        if editable:
            _session_edits.add(sid)
    try:
        yield editable
    finally:
        if editable:
            with _runs_lock:
                _session_edits.remove(sid)


def stop(sid: str, run_id: str | None = None) -> bool:
    """Dung ro rang luot dang chay cua phien (nut Dung); dong tab/doi trang KHONG goi ham nay."""
    r = lookup_run(sid, run_id)
    if not r or r.done:
        return False
    r.cancel.set()
    _wake_pending(sid)
    return True


def _wake_pending(sid: str) -> None:
    for pending in (_approvals.copy(), _questions.copy()):
        for entry in pending.values():
            if entry["sid"] == sid:
                entry["event"].set()


def lookup_run(sid: str, run_id: str | None = None) -> Run | None:
    with _runs_lock:
        _gc()
        run = _runs.get(sid)
        return run if run and (run_id is None or run.id == run_id) else None


def attach(sid: str, start: int = 0) -> Iterator[dict]:
    run = lookup_run(sid)
    if not run:
        yield {"type": "done"}
        return
    yield from run.tail(start)


def stream_chat(sid: str | None, text: str, provider: str | None, *, approver_override=None, source: str = "chat",
                only_tools: list[str] | None = None, attachments: list[str] | None = None, permission: str = "default",
                effort: str | None = None, docs: bool = False, temperature: float | None = None,
                max_tokens: int | None = None, detach: bool = False, system_extra: str = "", tool_allow: list[str] | None = None,
                assistant: str | None = None, kb_category_id: str | None = None, document_ids: list[str] | None = None) -> Iterator[dict]:
    """detach=True (giao dien web): dong ket noi khong dung agent; client noi lai bang attach(). Mac dinh (CLI/API/Telegram): dong ket noi thi dung."""
    if not sid or not sessions.get(sid):
        sid = sessions.create(text, source=source)
    error = ""
    with _runs_lock:
        _gc()
        if active(sid) or sid in _session_edits:
            error = "Phiên này đang có tác vụ. Hãy đợi xong rồi thử lại."
        elif assistant is not None and not sessions.set_assistant(sid, assistant):
            error = "Hãy bắt đầu phiên mới để đổi hồ sơ."
        else:
            track = detach and source == "chat"
            with db() as conn:
                count = conn.execute("SELECT COUNT(*) FROM messages WHERE session_id=?", (sid,)).fetchone()[0]
                run = Run(sid, text, attachments or [], count, document_ids)
                if track:
                    title = " ".join(text.split())[:100] or "Chat"
                    work_runs.begin(conn, run.id, "chat", title, session_id=sid)
            _runs[sid] = run
    if error:
        yield {"type": "session", "id": sid}
        yield {"type": "error", "message": error}
        yield {"type": "done"}
        return
    cancel = run.cancel

    def approver(kind: str, detail: str) -> bool:
        aid = uuid.uuid4().hex
        _approvals[aid] = {"event": threading.Event(), "ok": False, "sid": sid, "kind": kind, "detail": detail}
        run.push({"type": "approval", "id": aid, "kind": kind, "detail": detail})
        if not cancel.is_set():
            _approvals[aid]["event"].wait(APPROVAL_TIMEOUT)
        ok = _approvals.pop(aid)["ok"] and not cancel.is_set()
        run.push({"type": "approval_done", "id": aid, "ok": ok})
        return ok

    def asker(question: str, options: list[str], form: list[dict] | None = None) -> str:
        qid = uuid.uuid4().hex
        _questions[qid] = {"event": threading.Event(), "answer": "", "sid": sid, "question": question, "options": options, "form": form}
        run.push({"type": "question", "id": qid, "question": question, "options": options, **({"form": form} if form else {})})
        if not cancel.is_set():
            _questions[qid]["event"].wait(QUESTION_TIMEOUT)
        ans = _questions.pop(qid)["answer"] if not cancel.is_set() else ""
        run.push({"type": "question_done", "id": qid, "answer": ans})
        return ans

    def worker():
        try:
            agent.run_turn(sid, text, provider, approver_override or approver, run.push, cancel, only_tools, source, attachments, permission, effort, use_docs=docs, temperature=temperature, max_tokens=max_tokens, system_extra=system_extra, tool_allow=tool_allow,
                           asker=None if approver_override else asker, interactive_policy=detach and source == "chat" and approver_override is None, kb_category_id=kb_category_id, document_ids=document_ids)
        except Exception as e:  # loi bat ngo khong duoc lam treo luong SSE
            run.push({"type": "error", "message": f"{type(e).__name__}: {e}"})
        try:
            from nestor.services import checkpoints
            if (summary := checkpoints.finish(sid)):
                run.push({"type": "turn_summary", **summary})
        except Exception:  # noqa: BLE001 - tom tat thay doi khong duoc lam hong chat
            pass
        try:
            from nestor.services import habits
            habits.observe(sid, text, source)
        except Exception:  # noqa: BLE001 - gợi ý thói quen không được làm hỏng chat
            pass
        try:
            threading.Thread(target=_auto_name_session, args=(sid, text, provider), daemon=True).start()
        except Exception:
            pass
        try:
            if track:
                error = next((event["message"] for event in run.events if event["type"] == "error"), "")
                answer = next((event["content"] for event in reversed(run.events) if event["type"] == "assistant"), "")
                try:
                    files = _output_files(sid, run.events)
                except (OSError, ValueError):
                    files = []
                status = "cancelled" if cancel.is_set() else "error" if error else "ok"
                with db() as conn:
                    work_runs.finish(conn, run.id, status, error or answer, files)
        finally:
            run.push({"type": "done"})

    try:
        threading.Thread(target=worker, daemon=True).start()
    except RuntimeError as exc:
        if track:
            with db() as conn:
                work_runs.finish(conn, run.id, "error", str(exc))
        run.push({"type": "error", "message": str(exc)})
        run.push({"type": "done"})
    yield {"type": "session", "id": sid, "run_id": run.id}
    try:
        yield from run.tail(0)
    finally:
        if not detach:
            cancel.set()  # client ngat ket noi -> dung agent, tu choi cac xin phep dang cho
            _wake_pending(sid)
