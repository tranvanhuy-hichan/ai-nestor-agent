"""To cong tac da agent: trang thai song cua cac thanh vien va bang ghi chep chung (trong bo nho, giu 50 to gan nhat)."""
import threading
import time
import uuid

_teams: dict[str, dict] = {}
_lock = threading.Lock()
KEEP = 50


def create(goal: str, members: list[dict], session_id: str | None) -> dict:
    t = {"id": uuid.uuid4().hex[:8], "goal": goal, "status": "running", "created": time.time(), "session_id": session_id, "notes": {}, "result": "",
         "members": [{"role": m["role"], "task": m["task"], "status": "queued", "job_id": None, "result": "", "error": ""} for m in members], "review": {"status": "pending", "result": ""}}
    with _lock:
        _teams[t["id"]] = t
        for old in sorted(_teams, key=lambda k: _teams[k]["created"])[:-KEEP]:
            del _teams[old]
    return t


def get(tid: str) -> dict | None:
    return _teams.get(tid)


def list_all() -> list[dict]:
    return [{k: t[k] for k in ("id", "goal", "status", "created")} | {"members": len(t["members"])} for t in sorted(_teams.values(), key=lambda t: -t["created"])]


def note_write(tid: str, key: str, text: str, author: str = "") -> None:
    t = _teams.get(tid)
    if not t:
        raise KeyError(f"không có tổ công tác '{tid}'")
    with _lock:
        t["notes"][key[:60]] = {"text": text[:4000], "author": author, "ts": time.time()}


def note_read(tid: str, key: str = "") -> str:
    t = _teams.get(tid)
    if not t:
        raise KeyError(f"không có tổ công tác '{tid}'")
    if key:
        n = t["notes"].get(key)
        return n["text"] if n else f"chưa có ghi chép '{key}'"
    return "\n".join(f"[{k}] ({n['author'] or '?'}): {n['text']}" for k, n in t["notes"].items()) or "bảng ghi chép đang trống"


def latest_for_session(sid: str) -> dict | None:
    mine = [t for t in _teams.values() if t.get("session_id") == sid]
    return max(mine, key=lambda t: t["created"]) if mine else None
