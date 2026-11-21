"""Durable records for work launched from web chat or the automation scheduler."""
import json
import time

from nestor.core.db import db


def begin(conn, run_id, kind, title, *, job_id=None, session_id=None, trigger="manual"):
    conn.execute(
        """INSERT INTO work_runs(id, kind, job_id, title, session_id, trigger, status, started)
           VALUES(?, ?, ?, ?, ?, ?, 'running', ?)""",
        (run_id, kind, job_id, title, session_id, trigger, time.time()),
    )


def finish(conn, run_id, status, output="", files=()):
    conn.execute(
        """UPDATE work_runs SET status=?, finished=?, output=?, files=?
           WHERE id=? AND status='running'""",
        (status, time.time(), output[:4_000], json.dumps(list(files)[:30], ensure_ascii=False), run_id),
    )


def recover_interrupted():
    with db() as conn:
        conn.execute("UPDATE work_runs SET status='interrupted', finished=? WHERE status='running'", (time.time(),))


def recent(limit: int, *, job_id: str | None = None) -> list[dict]:
    with db() as conn:
        if job_id is None:
            rows = conn.execute(
                """SELECT w.*, s.id AS accessible_session FROM work_runs w LEFT JOIN sessions s ON s.id=w.session_id
                   ORDER BY w.status='running' DESC, w.started DESC LIMIT ?""",
                (limit,),
            )
        else:
            rows = conn.execute(
                """SELECT w.*, s.id AS accessible_session FROM work_runs w LEFT JOIN sessions s ON s.id=w.session_id
                   WHERE w.kind='cron' AND w.job_id=? ORDER BY w.started DESC LIMIT ?""",
                (job_id, limit),
            )
        result = []
        for row in rows:
            entry = dict(row)
            entry["session_id"] = entry.pop("accessible_session")
            entry["files"] = json.loads(entry["files"]) if entry["session_id"] else []
            result.append(entry)
        return result
