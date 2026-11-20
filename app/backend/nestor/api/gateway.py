"""Gateway telemetry, log streaming and lifecycle operations."""
import asyncio
import itertools
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import time
from collections import deque
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from threading import Lock

import httpx
import psutil
from fastapi import APIRouter, BackgroundTasks, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from ..cli import daemon
from ..cli import service as servicecmd
from ..core import config, db
from ..core.paths import LOG_FILE
from ..services import heartbeat, mcp_client, scheduler
from ..services.telegram_channel import channel as telegram
from ..services.zalo_channel import channel as zalo
from .system import health

AUTO = True
router = APIRouter()
_entries = deque(maxlen=500)
_ids = itertools.count(1)
_log_epoch = str(time.time_ns())
_restart_lock = Lock()
_release_url = "https://api.github.com/repos/tranvanhuy-hichan/ai-nestor-agent/releases/latest"
_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
_secret = re.compile(r"(?i)(/bot|[?&](?:secret|token|key)=|bearer\s+|(?:mcp[- ]session[- ]id|session id)\s*[:=]\s*)([^\s/?&]+)")


class GatewayLogHandler(logging.Handler):
    def emit(self, record):
        _entries.append({
            "id": next(_ids), "ts": record.created, "level": record.levelname,
            "source": record.name, "message": _secret.sub(r"\1[redacted]", record.getMessage())[:2000],
        })


def start_log_capture():
    handler = GatewayLogHandler()
    logger = logging.getLogger()
    previous = logger.level
    logger.setLevel(min(previous, logging.INFO))
    logger.addHandler(handler)
    # Uvicorn's base logger does not propagate.
    logging.getLogger("uvicorn").addHandler(handler)
    return handler, previous


def stop_log_capture(state):
    handler, previous = state
    logging.getLogger().removeHandler(handler)
    logging.getLogger("uvicorn").removeHandler(handler)
    logging.getLogger().setLevel(previous)
    handler.close()


def _restart_manager():
    if daemon.read_pid() == os.getpid():
        return "cli"
    if os.environ.get("INVOCATION_ID") and shutil.which("systemctl"):
        try:
            unit = subprocess.run(
                ["systemctl", "--user", "show", "nestor.service", "--property=MainPID", "--value"],
                capture_output=True, text=True, timeout=2,
            )
            if unit.stdout.strip() == str(os.getpid()):
                return "systemd"
        except (OSError, subprocess.TimeoutExpired):
            pass
    return None


def _autostart_path() -> Path:
    return servicecmd.unit_path() if servicecmd._system() == "Linux" else servicecmd.plist_path()


def _autostart_status() -> dict:
    """Co cai dat tu khoi dong (systemd user / launchd) chua, va hien dang bat hay tat."""
    system = servicecmd._system()
    if system not in ("Linux", "Darwin"):
        return {"supported": False, "installed": False, "enabled": False}
    path = _autostart_path()
    if not path.is_file():
        return {"supported": True, "installed": False, "enabled": False}
    if system == "Linux":
        r = servicecmd._run(["systemctl", "--user", "is-enabled", f"{servicecmd.NAME}.service"])
        enabled = r.stdout.strip() == "enabled"
    else:
        r = servicecmd._run(["launchctl", "print", f"gui/{os.getuid()}/{servicecmd.LABEL}"])
        enabled = r.returncode == 0
    return {"supported": True, "installed": True, "enabled": enabled}


@router.get("/gateway/autostart")
def autostart_status():
    return _autostart_status()


class AutostartBody(BaseModel):
    enabled: bool


@router.post("/gateway/autostart")
def set_autostart(b: AutostartBody):
    """Bat: cai/bat dich vu he thong (systemd user tren Linux, launchd tren macOS), chay cung may bai dang nhap.
    Tat: go dich vu do, tien trinh hien tai (neu dang chay qua service) khong bi dung ngay."""
    system = servicecmd._system()
    if system not in ("Linux", "Darwin"):
        raise HTTPException(409, "Hệ điều hành này chưa hỗ trợ tự khởi động cùng máy")
    state = daemon.read_state()
    host, port = state.get("host") or daemon.default_host(), state.get("port") or daemon.default_port()
    if b.enabled:
        path = _autostart_path()
        text = servicecmd.systemd_unit(host, port) if system == "Linux" else servicecmd.launchd_plist(host, port)
        if system == "Linux" and not shutil.which("systemctl"):
            raise HTTPException(409, "Không tìm thấy systemctl")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        if system == "Linux":
            steps = [["systemctl", "--user", "daemon-reload"], ["systemctl", "--user", "enable", f"{servicecmd.NAME}.service"]]
        else:
            steps = [["launchctl", "bootstrap", f"gui/{os.getuid()}", str(path)]]
        for cmd in steps:
            r = servicecmd._run(cmd)
            if r.returncode != 0:
                raise HTTPException(500, (r.stderr or r.stdout or "Lệnh thất bại").strip()[:500])
    else:
        path = _autostart_path()
        if path.is_file():
            if system == "Linux":
                servicecmd._run(["systemctl", "--user", "disable", f"{servicecmd.NAME}.service"])
            else:
                servicecmd._run(["launchctl", "bootout", f"gui/{os.getuid()}", str(path)])
            path.unlink(missing_ok=True)
            if system == "Linux":
                servicecmd._run(["systemctl", "--user", "daemon-reload"])
    return _autostart_status()


def current_version() -> str:
    try:
        return version("nestor-agent")
    except PackageNotFoundError:
        return health()["version"]


@router.get("/gateway")
def status():
    cfg = config.load()
    memory = psutil.virtual_memory()
    workspace = cfg.workspace_path()
    disk = shutil.disk_usage(workspace if workspace.exists() else db.DB_PATH.parent)
    db_size = 0
    for path in (db.DB_PATH, Path(f"{db.DB_PATH}-wal"), Path(f"{db.DB_PATH}-shm")):
        try:
            db_size += path.stat().st_size
        except OSError:
            continue
    hb = heartbeat.status()
    with db.db() as conn:
        background = {row["status"]: row["n"] for row in conn.execute(
            "SELECT status, COUNT(*) n FROM jobs WHERE status IN ('queued', 'running') GROUP BY status"
        )}
    return {
        **health(), "version": current_version(), "cpu": psutil.cpu_percent(interval=0.1),
        "memory_used": memory.total - memory.available, "memory_total": memory.total,
        "disk_used": disk.used, "disk_total": disk.total, "database_bytes": db_size,
        "restart_manager": _restart_manager(),
        "scheduler_running": scheduler.running(),
        "background": {"running": background.get("running", 0), "queued": background.get("queued", 0)},
        "channels": {
            "Telegram": {"enabled": cfg.channels.telegram.enabled, "running": telegram.status["running"]},
            "Zalo OA": {"enabled": cfg.channels.zalo.enabled, "running": zalo.status["running"]},
        },
        "heartbeat": {k: hb[k] for k in ("enabled", "running", "last_status", "next_run")},
        "mcp": {name: item["status"] for name, item in mcp_client.manager.status().items()},
    }


@router.get("/gateway/updates")
def updates():
    try:
        response = httpx.get(_release_url, timeout=5, follow_redirects=True)
        if response.status_code == 404:
            return {"current": current_version(), "latest": None, "available": False}
        response.raise_for_status()
        tag = response.json()["tag_name"]
        current = current_version()
        numeric_tag = re.fullmatch(r"v?(\d+)\.(\d+)\.(\d+)", tag)
        numeric_current = re.match(r"(\d+)\.(\d+)\.(\d+)", current)
        available = bool(numeric_tag and numeric_current
                         and tuple(map(int, numeric_tag.groups())) > tuple(map(int, numeric_current.groups())))
    except (httpx.HTTPError, ValueError, KeyError, TypeError) as exc:
        raise HTTPException(502, "Không kiểm tra được bản phát hành") from exc
    return {"current": current, "latest": tag, "available": available}


@router.post("/gateway/restart", status_code=202)
def restart(tasks: BackgroundTasks):
    manager = _restart_manager()
    if not manager:
        raise HTTPException(409, "Tiến trình này do môi trường triển khai quản lý")
    if not _restart_lock.acquire(blocking=False):
        raise HTTPException(409, "Gateway đang khởi động lại")

    def launch():
        try:
            if manager == "systemd":
                command = ["systemctl", "--user", "restart", "--no-block", "nestor.service"]
            else:
                command = [sys.executable, "-m", "nestor", "restart", "--no-build"]
            LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
            with LOG_FILE.open("ab") as output:
                process = subprocess.Popen(
                    command, env=daemon._server_env(), stdin=subprocess.DEVNULL,
                    stdout=output, stderr=subprocess.STDOUT, start_new_session=True,
                )
                process.wait()
        finally:
            _restart_lock.release()

    # Return the response before signaling Uvicorn, without keeping an ASGI background task alive.
    from threading import Thread
    tasks.add_task(lambda: Thread(target=launch, daemon=True).start())
    return {"ok": True}


def _snapshot():
    handler = next((h for h in logging.getLogger().handlers if isinstance(h, GatewayLogHandler)), None)
    if handler:
        handler.acquire()
    try:
        return list(_entries)
    finally:
        if handler:
            handler.release()


@router.get("/gateway/logs")
def logs(request: Request, level: str = "", q: str = ""):
    if level and level not in _levels:
        raise HTTPException(422, "Mức log không hợp lệ")

    epoch, _, previous = request.headers.get("last-event-id", "").partition(":")
    last_id = int(previous) if epoch == _log_epoch and previous.isdigit() and len(previous) <= 20 else 0
    needle = q.casefold()

    async def stream():
        cursor = last_id
        last_tick = 0
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline and not _restart_lock.locked() and not await request.is_disconnected():
            for entry in _snapshot():
                if entry["id"] <= cursor:
                    continue
                cursor = entry["id"]
                if (not level or entry["level"] == level) and needle in (entry["message"] + " " + entry["source"]).casefold():
                    yield f"id: {_log_epoch}:{cursor}\ndata: {json.dumps(entry, ensure_ascii=False)}\n\n"
            if last_tick % 15 == 0:
                yield ": keepalive\n\n"
            last_tick += 1
            await asyncio.sleep(1)

    return StreamingResponse(stream(), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
