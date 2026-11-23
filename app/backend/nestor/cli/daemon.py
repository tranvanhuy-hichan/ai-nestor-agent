"""Chay server nen: start / stop / restart / status / logs / dev / open (thay cho run.sh)."""
import json
import os
import shutil
import signal
import socket
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

import httpx

from ..core import config as cfgmod
from ..core.env import getenv
from ..core.paths import CODE_ROOT, DATA, DB_PATH, DIST, LOG_FILE, PID_FILE, ROOT
from .banner import available_skill_rows, banner_field, banner_heading, document_processing_rows, print_banner
from .ui import L, bad, bold, cyan, dim, green, info, ok, red, warn, yellow

STATE_FILE = DATA / "server.json"
BACKEND_DIR = Path(__file__).resolve().parents[2]  # thu muc chua goi `nestor` (de chay duoc ca khi chua pip install)


def default_host() -> str:
    return getenv("HOST") or "127.0.0.1"


def default_port() -> int:
    return int(getenv("PORT") or 8787)


def public_url(host: str, port: int) -> str:
    return f"http://{'127.0.0.1' if host in ('0.0.0.0', '::') else host}:{port}"


def _alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    cmdline = Path(f"/proc/{pid}/cmdline")
    if cmdline.exists():  # tranh nham voi tien trinh khac da lay lai so pid cu
        try:
            return b"uvicorn" in cmdline.read_bytes() or b"nestor" in cmdline.read_bytes()
        except OSError:
            return True
    return True


def read_pid() -> int | None:
    try:
        pid = int(PID_FILE.read_text().strip())
    except (OSError, ValueError):
        return None
    return pid if _alive(pid) else None


def read_state() -> dict:
    try:
        return json.loads(STATE_FILE.read_text())
    except (OSError, ValueError):
        return {}


def health(url: str, timeout: float = 1.5) -> dict | None:
    try:
        r = httpx.get(url + "/api/health", timeout=timeout)
        return r.json() if r.status_code == 200 else None
    except (httpx.HTTPError, ValueError):
        return None


def port_in_use(host: str, port: int) -> bool:
    probe = "127.0.0.1" if host in ("0.0.0.0", "::") else host
    with socket.socket() as s:
        s.settimeout(0.5)
        return s.connect_ex((probe, port)) == 0


def _cleanup() -> None:
    PID_FILE.unlink(missing_ok=True)
    STATE_FILE.unlink(missing_ok=True)


def _server_env() -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(filter(None, [str(BACKEND_DIR), env.get("PYTHONPATH", "")]))
    return env


def _tail(n: int) -> list[str]:
    try:
        return LOG_FILE.read_text(errors="replace").splitlines()[-n:]
    except OSError:
        return []


def ensure_frontend(build: bool = True) -> None:
    if (DIST / "index.html").exists():
        return
    web = CODE_ROOT / "frontend"
    if build and shutil.which("npm") and (web / "package.json").exists():
        info(L("Giao diện web chưa được build, đang build (lần đầu mất khoảng 1 phút)…", "The web UI is not built yet; building it (about a minute the first time)…"))
        for cmd in (["npm", "install", "--no-fund", "--no-audit"], ["npm", "run", "build"]):
            if subprocess.run(cmd, cwd=web, capture_output=True).returncode != 0:
                warn(L(f"Không build được giao diện ({' '.join(cmd)}). Server vẫn chạy, chỉ có API.", f"Could not build the UI ({' '.join(cmd)}). The server still runs, API only."))
                return
        ok(L("Đã build giao diện.", "UI built."))
    else:
        warn(L("Giao diện web chưa được build (cần Node.js: cd app/frontend && npm install && npm run build). Server vẫn chạy, chỉ có API.",
               "The web UI is not built (needs Node.js: cd app/frontend && npm install && npm run build). The server still runs, API only."))


def start(host: str, port: int, foreground: bool = False, build: bool = True) -> int:
    pid = read_pid()
    if pid:
        st = read_state()
        ok(L(f"Nestor Agent đang chạy (pid {pid}) tại {public_url(st.get('host', host), st.get('port', port))}", f"Nestor Agent is already running (pid {pid}) at {public_url(st.get('host', host), st.get('port', port))}"))
        return 0
    if port_in_use(host, port):
        bad(L(f"Cổng {port} đang được chương trình khác dùng. Dùng --port để chọn cổng khác, hoặc `nestor stop` nếu đó là Nestor.",
              f"Port {port} is already in use. Use --port to pick another one, or `nestor stop` if that is Nestor."))
        return 1
    DATA.mkdir(parents=True, exist_ok=True)
    ensure_frontend(build)
    cmd = [sys.executable, "-m", "uvicorn", "nestor.main:app", "--host", host, "--port", str(port)]
    if foreground:
        PID_FILE.write_text(str(os.getpid()))
        STATE_FILE.write_text(json.dumps({"host": host, "port": port, "started": time.time(), "pid": os.getpid()}))
        try:
            return subprocess.call(cmd, cwd=ROOT, env=_server_env())
        except KeyboardInterrupt:
            return 0
        finally:
            _cleanup()
    with open(LOG_FILE, "ab") as log:
        proc = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, cwd=ROOT, env=_server_env(), start_new_session=True)
    PID_FILE.write_text(str(proc.pid))
    STATE_FILE.write_text(json.dumps({"host": host, "port": port, "started": time.time(), "pid": proc.pid}))
    url = public_url(host, port)
    for _ in range(100):  # toi da ~25 giay
        if proc.poll() is not None:
            break
        if health(url):
            ok(L(f"Nestor Agent đã chạy (pid {proc.pid}): {bold(url)}", f"Nestor Agent is running (pid {proc.pid}): {bold(url)}"))
            print(dim(L("  Xem log: nestor logs -f   ·   Dừng: nestor stop   ·   Mở giao diện: nestor open",
                        "  Logs: nestor logs -f   ·   Stop: nestor stop   ·   Open the UI: nestor open")))
            if host not in ("127.0.0.1", "localhost") and not cfgmod.load().auth.password_hash:
                warn(L("Server đang mở ra ngoài localhost mà chưa đặt mật khẩu giao diện. Chạy `nestor onboard` hoặc đặt trong Cài đặt > Bảo mật.",
                       "The server is reachable beyond localhost but no interface password is set. Run `nestor onboard` or set one in Settings > Security."))
            return 0
        time.sleep(0.25)
    bad(L("Server không khởi động được. Log gần nhất:", "The server failed to start. Recent log:"))
    for line in _tail(15):
        print(dim("  " + line))
    if proc.poll() is None:
        proc.terminate()
    _cleanup()
    return 1


def stop() -> int:
    pid = read_pid()
    if not pid:
        _cleanup()
        st = read_state() or {}
        if health(public_url(st.get("host", default_host()), st.get("port", default_port()))):
            warn(L("Có một server đang chạy nhưng không do `nestor start` khởi động (service systemd, Docker?). Dùng `nestor service stop` hoặc docker compose down.",
                   "A server is running but was not started by `nestor start` (systemd service, Docker?). Use `nestor service stop` or docker compose down."))
            return 1
        info(L("Nestor Agent không chạy.", "Nestor Agent is not running."))
        return 0
    os.kill(pid, signal.SIGTERM)
    for _ in range(100):
        if not _alive(pid):
            break
        time.sleep(0.1)
    else:
        os.kill(pid, getattr(signal, "SIGKILL", signal.SIGTERM))
        warn(L("Server không tắt kịp, đã buộc dừng.", "The server did not exit in time and was killed."))
    _cleanup()
    ok(L("Đã dừng Nestor Agent.", "Nestor Agent stopped."))
    return 0


def restart(host: str, port: int, build: bool = True) -> int:
    st = read_state()
    stop()
    return start(st.get("host", host), st.get("port", port), build=build)


def status(as_json: bool = False) -> int:
    pid = read_pid()
    st = read_state()
    host, port = st.get("host", default_host()), st.get("port", default_port())
    url = public_url(host, port)
    h = health(url) if pid or port_in_use(host, port) else None
    cfg = cfgmod.load()
    sessions = 0
    try:
        import sqlite3

        sessions = sqlite3.connect(DB_PATH).execute("SELECT COUNT(*) FROM sessions").fetchone()[0] if DB_PATH.exists() else 0
    except Exception:  # noqa: BLE001
        pass
    data = {
        "running": bool(h), "pid": (h or {}).get("pid") or pid, "url": url, "version": (h or {}).get("version"),
        "uptime_s": int(time.time() - (h or {}).get("started", time.time())) if h else None,
        "managed_by_cli": bool(pid), "default_provider": cfg.default_provider,
        "model": cfg.providers[cfg.default_provider].model if cfg.default_provider in cfg.providers else None,
        "providers": list(cfg.providers), "sessions": sessions, "mcp_servers": len(cfg.mcp_servers),
        "telegram": cfg.channels.telegram.enabled, "heartbeat": cfg.heartbeat.enabled, "password": bool(cfg.auth.password_hash),
        "sandbox": cfg.agent.exec_sandbox, "home": str(ROOT),
    }
    if as_json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0 if data["running"] else 1
    enabled = L("bật", "on")
    disabled = L("tắt", "off")
    running = data["running"]
    state = green(L("● Đang chạy", "● Running")) if running else red(L("○ Đã dừng", "○ Stopped"))
    up = max(0, data["uptime_s"] or 0)
    uptime = f"{up // 3600}h {up % 3600 // 60:02d}m" if running else "—"
    manager = "nestor start" if data["managed_by_cli"] else (
        L("dịch vụ bên ngoài CLI", "external service") if running else "—"
    )
    password = green(L("đã đặt", "set")) if data["password"] else yellow(L("chưa đặt", "not set"))
    sidebar = (
        banner_heading(f"{data['default_provider']} · {data['model'] or '—'}"),
    )
    details = [
        banner_heading("Gateway"),
        banner_field(L("Trạng thái", "Status"), state),
        banner_field("URL", cyan(url)),
        banner_field("PID", str(data["pid"] or "—")),
        banner_field(L("Phiên bản", "Version"), data["version"] or "—"),
        banner_field(L("Thời gian chạy", "Uptime"), uptime),
        banner_field(L("Quản lý", "Managed by"), manager),
        "",
        banner_heading(L("Nhà cung cấp và tích hợp", "Providers and integrations")),
        banner_field(L("Nhà cung cấp", "Providers"), ", ".join(data["providers"]) or "—"),
        banner_field(L("Hội thoại", "Conversations"), str(sessions)),
        banner_field(L("Máy chủ MCP đã cấu hình", "Configured MCP servers"), str(data["mcp_servers"])),
        banner_field("Telegram", green(enabled) if data["telegram"] else dim(disabled)),
        banner_field("Heartbeat", green(enabled) if data["heartbeat"] else dim(disabled)),
        "",
        banner_heading(L("Bảo mật", "Security")),
        banner_field(L("Mật khẩu giao diện", "Interface password"), password),
        banner_field("Sandbox", data["sandbox"]),
        "",
        banner_heading(L("Kỹ năng và tài liệu", "Skills and documents")),
        *document_processing_rows(cfg),
        *available_skill_rows(cfg, max_categories=1, compact=True),
    ]
    if running:
        tip = L("  nestor open  Giao diện web", "  nestor open  Web UI")
        if data["managed_by_cli"]:
            tip += L("   ·   nestor logs  Nhật ký", "   ·   nestor logs  Logs")
    else:
        tip = L("  nestor start  Khởi động gateway", "  nestor start  Start the gateway")
    print_banner(
        L("Nestor Agent · Trạng thái", "Nestor Agent · Status"),
        [(line, "") for line in details], tip, sidebar=sidebar,
        sidebar_path=(L("Dữ liệu", "Data"), data["home"]),
    )
    return 0 if data["running"] else 1


def logs(follow: bool, n: int) -> int:
    if not LOG_FILE.exists():
        info(L("Chưa có log (server chưa từng chạy bằng `nestor start`). Nếu chạy bằng systemd: journalctl --user -u nestor -f",
               "No log yet (the server has not run via `nestor start`). With systemd: journalctl --user -u nestor -f"))
        return 0
    for line in _tail(n):
        print(line)
    if follow:
        try:
            with open(LOG_FILE, errors="replace") as f:
                f.seek(0, os.SEEK_END)
                while True:
                    line = f.readline()
                    if line:
                        print(line, end="", flush=True)
                    else:
                        time.sleep(0.4)
        except KeyboardInterrupt:
            pass
    return 0


def open_ui(host: str, port: int) -> int:
    st = read_state()
    url = public_url(st.get("host", host), st.get("port", port))
    if not health(url):
        bad(L("Server chưa chạy. Bật bằng: nestor start", "The server is not running. Start it with: nestor start"))
        return 1
    from .banner import print_open_banner
    print_open_banner(url)
    webbrowser.open(url)
    return 0


def dev(port: int) -> int:
    """Chay che do phat trien: backend tu nap lai + Vite (cong 5173)."""
    web = CODE_ROOT / "frontend"
    if not shutil.which("npm") or not (web / "package.json").exists():
        bad(L("Cần Node.js và thư mục app/frontend/ để chạy chế độ phát triển.", "Node.js and the app/frontend/ folder are required for dev mode."))
        return 1
    env = _server_env()
    env["NESTOR_DEV_ORIGINS"] = "http://localhost:5173,http://127.0.0.1:5173"
    api = subprocess.Popen([sys.executable, "-m", "uvicorn", "nestor.main:app", "--reload", "--reload-dir", str(BACKEND_DIR / "nestor"), "--port", str(port)], cwd=ROOT, env=env)
    ui = subprocess.Popen(["npm", "run", "dev"], cwd=web)
    info(L("Chế độ phát triển: giao diện http://localhost:5173 (Ctrl+C để dừng cả hai)", "Dev mode: UI at http://localhost:5173 (Ctrl+C stops both)"))
    try:
        api.wait()
    except KeyboardInterrupt:
        pass
    finally:
        for p in (ui, api):
            p.terminate()
    return 0
