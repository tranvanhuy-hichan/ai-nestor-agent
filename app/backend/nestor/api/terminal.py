"""Interactive terminal for explicitly enabled Nestor installations."""
import asyncio
import errno
import json
import os
import signal
import struct
import subprocess
import sys

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..core import config
from ..core.env import getenv
from ..core.paths import FROZEN
from ..services import assistants, auth, sessions, workfiles

AUTO = True
router = APIRouter()
_active = 0


def enabled() -> bool:
    return os.name == "posix" and getenv("WEB_TERMINAL") == "1" and bool(config.load().auth.password_hash)


@router.get("/terminal/status")
def terminal_status():
    return {"enabled": enabled()}


@router.websocket("/terminal")
async def terminal(ws: WebSocket, session: str = ""):
    global _active
    host = ws.headers.get("host", "")
    origin = ws.headers.get("origin", "")
    expected = ("https://" if ws.url.scheme == "wss" else "http://") + host
    from ..main import ALLOWED_HOSTS, DEV_ORIGINS
    name = host.split("]")[0] + "]" if host.startswith("[") else host.split(":")[0]
    if (name not in ALLOWED_HOSTS or not origin or (origin != expected and origin not in DEV_ORIGINS)
            or not enabled() or not auth.verify_token(ws.cookies.get(auth.COOKIE))):
        return await ws.close(1008)
    session_row = sessions.get(session) if session else None
    if _active >= 4 or (session and not session_row):
        return await ws.close(1008)

    import fcntl
    import pty
    import termios

    cfg = config.load()
    cwd = workfiles.workdir_for(cfg, session) if session else cfg.workspace_path()
    cwd.mkdir(parents=True, exist_ok=True)
    command = [sys.executable, "--terminal-shell"] if FROZEN else [sys.executable, "-m", "nestor.services.terminal_child"]
    profile = assistants.scoped_profile(session_row.get("assistant")) if session_row else None
    profile_env = assistants.profile_env(profile) if profile and profile["scope_key"] == session_row.get("assistant_scope") else {}
    env = {**os.environ, **profile_env, "TERM": "xterm-256color"}
    _active += 1
    process = fd = None
    try:
        await ws.accept()
        fd, slave = pty.openpty()
        try:
            fcntl.ioctl(slave, termios.TIOCSWINSZ, struct.pack("HHHH", 24, 80, 0, 0))
            process = subprocess.Popen(
                command, stdin=slave, stdout=slave, stderr=slave, cwd=cwd, env=env, start_new_session=True,
            )
        finally:
            os.close(slave)
        os.set_blocking(fd, False)
        loop = asyncio.get_running_loop()

        async def wait_fd(write=False):
            ready = loop.create_future()
            add, remove = (loop.add_writer, loop.remove_writer) if write else (loop.add_reader, loop.remove_reader)
            add(fd, lambda: ready.done() or ready.set_result(None))
            try:
                await ready
            finally:
                remove(fd)

        async def output():
            while True:
                await wait_fd()
                try:
                    data = os.read(fd, 16384)
                except BlockingIOError:
                    continue
                except OSError as exc:
                    if exc.errno == errno.EIO:
                        return
                    raise
                if not data:
                    return
                await ws.send_bytes(data)

        async def input_():
            while True:
                event = await ws.receive()
                if event["type"] == "websocket.disconnect":
                    return
                data = event.get("bytes")
                if data is not None:
                    if len(data) > 65536:
                        return
                    while data:
                        await wait_fd(write=True)
                        try:
                            data = data[os.write(fd, data):]
                        except BlockingIOError:
                            continue
                elif len(event.get("text") or "") <= 100:
                    try:
                        size = json.loads(event.get("text") or "")
                        rows, cols = int(size["rows"]), int(size["cols"])
                    except (ValueError, TypeError, KeyError, OverflowError):
                        continue
                    if 1 <= rows <= 500 and 1 <= cols <= 1000:
                        fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", rows, cols, 0, 0))

        tasks = [asyncio.create_task(output()), asyncio.create_task(input_())]
        try:
            done, _ = await asyncio.wait(tasks, timeout=3600, return_when=asyncio.FIRST_COMPLETED)
            for task in done:
                task.result()
        finally:
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
    except (OSError, WebSocketDisconnect):
        pass
    finally:
        _active -= 1
        if fd is not None:
            os.close(fd)
        if process is not None:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            await asyncio.to_thread(process.wait)
    if ws.client_state.name != "DISCONNECTED":
        await ws.close()
