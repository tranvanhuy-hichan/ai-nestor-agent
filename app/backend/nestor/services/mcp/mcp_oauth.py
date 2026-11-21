"""OAuth 2.1 cho MCP server tu xa (Notion, Canva, Linear...): token luu MA HOA, dang nhap qua trinh duyet.

SDK MCP lo phan giao thuc (kham pha may chu cap quyen, dang ky client dong, PKCE, doi ma lay token, lam moi token). Phan cua Nestor:
  Store : noi luu client + token (bang kv, ma hoa bang cung khoa chu voi API key)
  Flow  : redirect_handler ghi lai URL cap quyen cho giao dien; callback_handler cho ma tra ve tu /api/mcp/oauth/callback
"""
import asyncio
import json
import logging
import threading
import time
from urllib.parse import parse_qs, urlparse

from mcp.client.auth import TokenStorage
from mcp.shared.auth import AuthorizationCodeResult, OAuthClientInformationFull, OAuthClientMetadata, OAuthToken

from nestor.core import secrets
from nestor.core.db import db

LOGIN_TIMEOUT = 300  # so giay cho nguoi dung bam "Cho phep" tren trang cua nha cung cap
CALLBACK_PATH = "/api/mcp/oauth/callback"


class NeedsAuth(Exception):
    """Server can dang nhap nhung dang o che do khong tuong tac (khoi dong, ket noi lai): giao dien se hien nut 'Dang nhap'."""


class _NeedsAuthFilter(logging.Filter):
    """Loc bo log traceback cua SDK MCP khi gap NeedsAuth (day la luong chuyen huong binh thuong, khong phai loi)."""

    def filter(self, record: logging.LogRecord) -> bool:
        if record.exc_info and issubclass(type(record.exc_info[1]), NeedsAuth):
            return False
        return True


logging.getLogger("mcp.client.auth.oauth2").addFilter(_NeedsAuthFilter())
logging.getLogger("mcp.client.auth.oauth").addFilter(_NeedsAuthFilter())


class Store(TokenStorage):
    """Client dang ky dong + token cua mot MCP server, luu trong bang kv duoi dang JSON da ma hoa."""

    def __init__(self, name: str) -> None:
        self.key = f"mcp_oauth:{name}"

    def _load(self) -> dict:
        with db() as c:
            r = c.execute("SELECT value FROM kv WHERE key=?", (self.key,)).fetchone()
        if not r:
            return {}
        try:
            return json.loads(secrets.decrypt(r["value"], f"mcp_oauth:{self.key}") or "{}")
        except json.JSONDecodeError:
            return {}

    def _save(self, d: dict) -> None:
        raw = json.dumps(d)
        with db() as c:
            c.execute("INSERT OR REPLACE INTO kv(key,value) VALUES(?,?)", (self.key, secrets.encrypt(raw) if secrets.enabled() else raw))

    async def get_tokens(self) -> OAuthToken | None:
        t = self._load().get("tokens")
        return OAuthToken.model_validate(t) if t else None

    async def set_tokens(self, tokens: OAuthToken) -> None:
        d = self._load()
        d["tokens"], d["saved"] = tokens.model_dump(mode="json"), time.time()
        self._save(d)

    async def get_client_info(self) -> OAuthClientInformationFull | None:
        c = self._load().get("client")
        return OAuthClientInformationFull.model_validate(c) if c else None

    async def set_client_info(self, client_info: OAuthClientInformationFull) -> None:
        d = self._load()
        d["client"] = client_info.model_dump(mode="json")
        self._save(d)

    # ---- tien ich dong bo cho API
    def logged_in(self) -> bool:
        return bool(self._load().get("tokens"))

    def redirect_base(self) -> str:
        return self._load().get("redirect_base", "")

    def use_redirect_base(self, base: str) -> None:
        """Client dang ky gan voi redirect_uri; doi dia chi/cong thi phai dang ky lai (va dang nhap lai)."""
        d = self._load()
        if d.get("redirect_base") != base:
            d = {"redirect_base": base}
            self._save(d)

    def clear(self) -> None:
        with db() as c:
            c.execute("DELETE FROM kv WHERE key=?", (self.key,))


_pending: dict[str, tuple[asyncio.AbstractEventLoop, asyncio.Future]] = {}
_lock = threading.Lock()


class Flow:
    """Mot lan ket noi: neu interactive thi cho nguoi dung dang nhap, neu khong thi bao NeedsAuth."""

    def __init__(self, interactive: bool, on_url) -> None:
        self.interactive, self.on_url, self.state = interactive, on_url, ""

    async def redirect(self, url: str) -> None:
        if not self.interactive:
            raise NeedsAuth()
        self.state = parse_qs(urlparse(url).query).get("state", [""])[0]
        loop = asyncio.get_running_loop()
        with _lock:
            _pending[self.state] = (loop, loop.create_future())
        self.on_url(url)

    async def callback(self) -> AuthorizationCodeResult:
        with _lock:
            _, fut = _pending[self.state]
        try:
            return await asyncio.wait_for(fut, LOGIN_TIMEOUT)
        except asyncio.TimeoutError:
            raise RuntimeError(f"quá {LOGIN_TIMEOUT}s không thấy đăng nhập xong") from None
        finally:
            with _lock:
                _pending.pop(self.state, None)


def complete(state: str, code: str = "", error: str = "", iss: str = "") -> bool:
    """Goi tu /api/mcp/oauth/callback (thread khac): tra ma (hoac loi) cho ket noi dang cho. False neu khong co ket noi nao dang cho."""
    with _lock:
        entry = _pending.get(state)
    if not entry:
        return False
    loop, fut = entry

    def done() -> None:
        if fut.done():
            return
        if error or not code:
            fut.set_exception(RuntimeError(f"nhà cung cấp từ chối đăng nhập: {error or 'không có mã'}"))
        else:
            fut.set_result(AuthorizationCodeResult(code=code, state=state, iss=iss or None))

    loop.call_soon_threadsafe(done)
    return True


def resolve_client_metadata(name: str, url: str, base: str, scope: str | None = None) -> OAuthClientMetadata:
    """Xây dựng OAuthClientMetadata kèm các tinh chỉnh cho từng nhà cung cấp (workarounds từ Hermes Agent).
    - Figma: yêu cầu client_name nằm trong allowlist của DCR ('Claude Code' hoặc 'Codex'), đồng thời bắt buộc client_secret_post.
    - Slack / HubSpot / Box: tương thích client_name.
    """
    client_name = "Nestor Agent"
    auth_method = "none"
    server_lower = (name or "").lower()
    url_lower = (url or "").lower()

    if "figma.com" in url_lower or server_lower == "figma":
        client_name = "Claude Code"
        auth_method = "client_secret_post"
        scope = scope or "mcp:connect"
    elif "slack.com" in url_lower or server_lower == "slack":
        client_name = "Claude Code"
    elif "box.com" in url_lower or server_lower == "box":
        client_name = "Claude Code"

    return OAuthClientMetadata(
        client_name=client_name,
        redirect_uris=[base + CALLBACK_PATH],
        grant_types=["authorization_code", "refresh_token"],
        response_types=["code"],
        token_endpoint_auth_method=auth_method,
        scope=scope or None,
    )
