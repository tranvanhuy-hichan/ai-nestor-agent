"""Automations: chay prompt theo lich cron (khong co nguoi duyet -> exec/ngoai workspace bi tu choi)."""
import threading
import time
import uuid

from croniter import croniter

from nestor.core import config as cfgmod
from nestor.core.db import db
from nestor.services import agent, notifications, sessions, workfiles

from . import work_runs

TICK = 15
_stop = threading.Event()
_thread: threading.Thread | None = None


class ScheduleError(ValueError):
    pass


def next_run(schedule: str, base: float | None = None) -> float:
    if not croniter.is_valid(schedule):
        raise ScheduleError(f"biểu thức cron không hợp lệ: {schedule}")
    return croniter(schedule, base or time.time()).get_next(float)


def list_jobs() -> list[dict]:
    with db() as c:
        return [dict(r) | {"enabled": bool(r["enabled"]), "notify": bool(r["notify"])} for r in c.execute("SELECT * FROM cron_jobs ORDER BY name")]


def save_job(job: dict, job_id: str | None = None) -> str:
    nxt = next_run(job["schedule"])
    with db() as c:
        if job_id:
            c.execute("UPDATE cron_jobs SET name=?,schedule=?,prompt=?,provider=?,enabled=?,next_run=?,notify=? WHERE id=?",
                      (job["name"], job["schedule"], job["prompt"], job.get("provider"), int(job["enabled"]), nxt, int(job.get("notify", True)), job_id))
        else:
            job_id = uuid.uuid4().hex[:8]
            c.execute("INSERT INTO cron_jobs(id,name,schedule,prompt,provider,enabled,next_run,notify) VALUES(?,?,?,?,?,?,?,?)",
                      (job_id, job["name"], job["schedule"], job["prompt"], job.get("provider"), int(job["enabled"]), nxt, int(job.get("notify", True))))
    return job_id


def delete_job(job_id: str) -> None:
    with db() as c:
        c.execute("DELETE FROM cron_jobs WHERE id=?", (job_id,))


def _claim(job_id: str, scheduled: bool):
    with db() as conn:
        conn.execute("BEGIN IMMEDIATE")
        job = conn.execute("SELECT * FROM cron_jobs WHERE id=?", (job_id,)).fetchone()
        if not job:
            raise ScheduleError("không có việc tự động này")
        now = time.time()
        if scheduled and (not job["enabled"] or job["next_run"] is None or job["next_run"] > now):
            return None
        if conn.execute("SELECT 1 FROM work_runs WHERE job_id=? AND kind='cron' AND status='running'", (job_id,)).fetchone():
            if scheduled:
                return None
            raise ScheduleError("việc tự động đang chạy")
        run_id = uuid.uuid4().hex
        work_runs.begin(conn, run_id, "cron", job["name"], job_id=job_id,
                        trigger="scheduled" if scheduled else "manual")
        if scheduled:
            conn.execute("UPDATE cron_jobs SET next_run=? WHERE id=?", (next_run(job["schedule"], now), job_id))
        return run_id, job, now


def _execute(run_id, job, started):
    sid = None
    error = ""
    output = ""
    files = []

    def collect(event):
        nonlocal error, output
        if event["type"] == "error" and not error:
            error = event["message"]
        elif event["type"] == "assistant":
            output = event["content"]

    try:
        sid = sessions.create(f"⏱ {job['name']}", source="cron")
        with db() as conn:
            conn.execute("UPDATE work_runs SET session_id=? WHERE id=?", (sid, run_id))
        agent.run_turn(sid, job["prompt"], job["provider"], lambda kind, detail: False, collect, source="cron")
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
    if sid:
        try:
            base = workfiles.workdir_for(cfgmod.load(), sid)
            files = [item["path"] for item in workfiles.tree(base) if not item["dir"]]
        except OSError:
            pass
    status = "error" if error else "ok"
    with db() as conn:
        work_runs.finish(conn, run_id, status, error or output, files)
        conn.execute("UPDATE cron_jobs SET last_run=?, last_status=?, last_output=? WHERE id=?",
                     (started, status, (error or output)[:2_000], job["id"]))
    if job["notify"] and (error or output):
        notifications.add(f"Automation: {job['name']}" + (" (lỗi)" if error else ""),
                          error or output, source="cron", session_id=sid)


def start_job(job_id: str, *, scheduled: bool = False) -> str | None:
    claim = _claim(job_id, scheduled)
    if claim is None:
        return None
    try:
        threading.Thread(target=_execute, args=claim, daemon=True).start()
    except RuntimeError as exc:
        with db() as conn:
            work_runs.finish(conn, claim[0], "error", str(exc))
        raise ScheduleError(str(exc)) from exc
    return claim[0]


def _loop() -> None:
    while not _stop.wait(TICK):
        with db() as conn:
            due = [r["id"] for r in conn.execute("SELECT id FROM cron_jobs WHERE enabled=1 AND next_run<=?", (time.time(),))]
        for job_id in due:
            try:
                start_job(job_id, scheduled=True)
            except ScheduleError:
                continue


def running() -> bool:
    return not _stop.is_set() and _thread is not None and _thread.is_alive()


def start() -> None:
    global _thread
    if running():
        return
    _stop.clear()
    _thread = threading.Thread(target=_loop, daemon=True, name="scheduler")
    _thread.start()


def stop() -> None:
    _stop.set()
    if _thread:
        _thread.join(timeout=1)
