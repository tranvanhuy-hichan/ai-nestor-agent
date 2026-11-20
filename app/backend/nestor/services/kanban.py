"""Kanban ca nhan: the 'viec can lam' nhe (chua giao agent) + giao viec bang jobs.py co san.
Cot hien thi: todo (the o day, chua chay) -> running/blocked/done (suy ra tu trang thai job that su).
Khong co nhieu profile/worker nhu Hermes: day la bang mot nguoi dung, giao viec la tao 1 job nen."""
import time
import uuid

from ..core.db import db
from . import jobs


def _row(r) -> dict:
    return dict(r)


def list_cards() -> list[dict]:
    with db() as c:
        rows = c.execute("SELECT * FROM kanban_cards ORDER BY sort").fetchall()
    return [_row(r) for r in rows]


def get(card_id: str) -> dict | None:
    with db() as c:
        r = c.execute("SELECT * FROM kanban_cards WHERE id=?", (card_id,)).fetchone()
    return _row(r) if r else None


def create(title: str, body: str = "", role: str = "") -> str:
    cid = uuid.uuid4().hex[:8]
    now = time.time()
    with db() as c:
        top = c.execute("SELECT MIN(sort) m FROM kanban_cards").fetchone()["m"]
        sort = (top - 1) if top is not None else 0.0
        c.execute("INSERT INTO kanban_cards(id,title,body,role,sort,created,updated) VALUES(?,?,?,?,?,?,?)",
                  (cid, title.strip()[:200], body, role, sort, now, now))
    return cid


def update(card_id: str, **fields) -> None:
    if not fields:
        return
    fields["updated"] = time.time()
    keys = ", ".join(f"{k}=?" for k in fields)
    with db() as c:
        c.execute(f"UPDATE kanban_cards SET {keys} WHERE id=?", (*fields.values(), card_id))


def reorder(card_id: str, before_id: str | None) -> None:
    """Dat card_id ngay truoc before_id (None = cuoi danh sach) bang cach chen sort giua hai lang gieng."""
    with db() as c:
        rows = c.execute("SELECT id, sort FROM kanban_cards WHERE id != ? ORDER BY sort", (card_id,)).fetchall()
        sorts = [r["sort"] for r in rows]
        ids = [r["id"] for r in rows]
        if before_id and before_id in ids:
            i = ids.index(before_id)
            new_sort = sorts[i] - 1 if i == 0 else (sorts[i - 1] + sorts[i]) / 2
        else:
            new_sort = (sorts[-1] + 1) if sorts else 0.0
        c.execute("UPDATE kanban_cards SET sort=?, updated=? WHERE id=?", (new_sort, time.time(), card_id))


def delete(card_id: str) -> bool:
    card = get(card_id)
    if not card:
        return False
    with db() as c:
        c.execute("DELETE FROM kanban_cards WHERE id=?", (card_id,))
    return True


def dispatch(card_id: str, permission: str = "default", provider: str | None = None) -> dict:
    """Giao the cho Nestor: tao job nen (jobs.py) voi tieu de/noi dung cua the, gan job_id vao the."""
    card = get(card_id)
    if not card:
        raise jobs.JobError("không có thẻ này")
    if card["job_id"]:
        job = jobs.get(card["job_id"])
        if job and job["status"] in jobs.ACTIVE:
            raise jobs.JobError("thẻ này đang được xử lý")
    goal = card["body"].strip() or card["title"]
    jid = jobs.start_background(goal, kind="task", title=card["title"], role=card["role"] or "general", permission=permission, provider=provider)
    update(card_id, job_id=jid)
    return {"job_id": jid}


def board() -> list[dict]:
    """The 'todo' (chua giao hoac job da ket thuc bi xoa) hoa cung trang thai job hien hanh, de UI ve 1 bang Kanban."""
    cards = list_cards()
    jmap = {j["id"]: j for j in jobs.list_jobs(limit=500)}
    out = []
    for c in cards:
        job = jmap.get(c["job_id"]) if c["job_id"] else None
        if not job:
            status = "todo"
        elif job["status"] in jobs.ACTIVE:
            status = "running"
        elif job["status"] == "done":
            status = "done"
        else:  # failed | cancelled | interrupted
            status = "blocked"
        out.append({**c, "status": status, "job": job})
    return out
