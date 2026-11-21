"""Kenh Zalo OA: Zalo goi webhook (POST /api/channels/zalo/webhook) -> agent -> tra loi qua API tin nhan tu van (cs)."""
import hashlib
import hmac
import logging
import threading
import time

import httpx

from nestor.core import config as cfgmod
from nestor.core.db import db
from nestor.services import chat_runner, notifications, pairing, sessions, workfiles
from .telegram_channel import KIND_LABEL, clean_reply

log = logging.getLogger("zalo")
API_BASE = "https://openapi.zalo.me"  # test co the doi sang server gia
OAUTH_BASE = "https://oauth.zaloapp.com"
CHUNK = 1900  # Zalo gioi han ~2000 ky tu moi tin
TOKEN_EXPIRED = {-216, -124, -233}  # access_token het han / khong hop le

def verify(cfg: cfgmod.ZaloCfg, body: bytes, signature: str, timestamp: str, query_secret: str) -> bool:
    """Chap nhan khi chu ky X-ZEvent-Signature dung (sha256(app_id + body + timestamp + secret)) hoac ?secret= khop. Chua dat webhook_secret => tu choi het."""
    if not cfg.webhook_secret:
        return False
    if query_secret and hmac.compare_digest(query_secret, cfg.webhook_secret):
        return True
    if signature:
        want = hashlib.sha256(f"{cfg.app_id}{body.decode(errors='replace')}{timestamp}{cfg.webhook_secret}".encode()).hexdigest()
        return hmac.compare_digest(signature.removeprefix("mac="), want)
    return False


def _chunks(text: str) -> list[str]:
    return [text[i:i + CHUNK] for i in range(0, len(text), CHUNK)] or ["(không có nội dung)"]


class ZaloChannel:
    def __init__(self) -> None:
        self.cfg = cfgmod.ZaloCfg()
        self.status = {"running": False, "error": "", "oa": ""}
        self._locks: dict[str, threading.Lock] = {}
        self._pending: dict[str, str] = {}  # user_id -> id yeu cau xin phep dang cho
        notifications.listeners.append(self._notify)

    def apply(self, cfg: cfgmod.ZaloCfg) -> None:
        self.cfg = cfg
        ok = cfg.enabled and bool(cfg.access_token or cfg.refresh_token)
        self.status = {"running": ok, "error": "" if ok or not cfg.enabled else "thiếu access token", "oa": cfg.oa_id if ok else ""}

    # ---- goi API
    def refresh(self) -> bool:
        cfg = cfgmod.load()
        z = cfg.channels.zalo
        if not (z.app_id and z.app_secret and z.refresh_token):
            return False
        r = httpx.post(f"{OAUTH_BASE}/v4/oa/access_token", headers={"secret_key": z.app_secret}, data={"app_id": z.app_id, "grant_type": "refresh_token", "refresh_token": z.refresh_token}, timeout=20).json()
        if not r.get("access_token"):
            self.status["error"] = f"làm mới token thất bại: {r.get('error_name') or r.get('error_description') or r}"[:200]
            return False
        z.access_token, z.refresh_token = r["access_token"], r.get("refresh_token") or z.refresh_token
        cfgmod.save(cfg)
        self.cfg = z
        self.status["error"] = ""
        return True

    def api(self, path: str, body: dict) -> dict:
        for attempt in range(2):
            r = httpx.post(f"{API_BASE}{path}", headers={"access_token": self.cfg.access_token}, json=body, timeout=30).json()
            if r.get("error", 0) in TOKEN_EXPIRED and attempt == 0 and self.refresh():
                continue
            if r.get("error", 0) != 0:
                raise RuntimeError(f"Zalo {path}: {r.get('message') or r}")
            return r
        raise RuntimeError("Zalo: không làm mới được token")

    def say(self, user_id: str, text: str) -> None:
        for part in _chunks(clean_reply(text)):
            self.api("/v3.0/oa/message/cs", {"recipient": {"user_id": user_id}, "message": {"text": part}})

    # ---- nhan tin
    def handle_event(self, event: dict) -> None:
        """Goi tu webhook (trong thread rieng)."""
        try:
            if event.get("event_name") != "user_send_text":
                return
            uid = str((event.get("sender") or {}).get("id") or "")
            text = ((event.get("message") or {}).get("text") or "").strip()
            if uid and text:
                self._handle(uid, text)
        except Exception as e:  # noqa: BLE001 - mot tin loi khong duoc lam hong webhook
            log.warning("zalo handle: %s", e)
            try:
                self.say(uid, f"⚠ Lỗi khi xử lý: {str(e)[:300]}")
            except Exception:  # noqa: BLE001
                pass

    def _link(self, uid: str) -> str | None:
        with db() as c:
            r = c.execute("SELECT session_id FROM channel_links WHERE channel='zalo' AND external_id=?", (uid,)).fetchone()
        return r["session_id"] if r and sessions.get(r["session_id"]) else None

    def _handle(self, uid: str, text: str) -> None:
        z = cfgmod.load().channels.zalo
        self.cfg = z
        if text.lower().startswith("/id"):
            return self.say(uid, f"ID Zalo của bạn: {uid}")
        if text.lower().startswith("/pair"):
            if uid in z.allowed_users:
                return self.say(uid, "Tài khoản đã được cấp quyền.")
            if pairing.submit("zalo", text[5:].strip(), uid):
                return self.say(uid, "Đã gửi yêu cầu. Hãy duyệt trong giao diện web Nestor.")
            return self.say(uid, "Mã ghép đôi sai hoặc đã hết hạn. Tạo mã mới trong giao diện, mục Tích hợp > Kênh chat.")
        if uid not in z.allowed_users:
            return self.say(uid, "Bạn chưa được phép dùng trợ lý này. Tạo mã ghép đôi trong giao diện web rồi gửi: /pair <mã>")
        pend = self._pending.pop(uid, None)
        if pend:  # dang cho xin phep: tra loi "ok/dong y" = cho phep, con lai = tu choi
            ok = text.strip().lower() in ("ok", "đồng ý", "dong y", "cho phép", "cho phep", "có", "co", "yes", "y")
            chat_runner.resolve_approval(pend, ok)
            if ok or text.strip().lower() in ("không", "khong", "no", "n", "từ chối", "tu choi"):
                return
        if text.lower().startswith("/new"):
            with db() as c:
                c.execute("DELETE FROM channel_links WHERE channel='zalo' AND external_id=?", (uid,))
            return self.say(uid, "Đã bắt đầu hội thoại mới.")
        if text.lower().startswith(("/help", "/start")):
            return self.say(uid, "Cứ nhắn tin để giao việc. Lệnh: /new (hội thoại mới), /id, /help. Khi tôi xin phép, trả lời 'ok' để cho phép hoặc 'không' để từ chối.")
        with self._locks.setdefault(uid, threading.Lock()):
            self._run(uid, text)

    def _run(self, uid: str, text: str) -> None:
        sid = self._link(uid)
        if not sid:
            sid = sessions.create(text[:40] or "Zalo", source="zalo")
            with db() as c:
                c.execute("INSERT OR REPLACE INTO channel_links(channel,external_id,session_id) VALUES('zalo',?,?)", (uid, sid))
        base = workfiles.session_dir(cfgmod.load(), sid)
        before = {t["path"]: t["mtime"] for t in workfiles.tree(base) if not t["dir"]}
        reply = error = ""
        for ev in chat_runner.stream_chat(sid, text, None, source="zalo"):
            if ev["type"] == "approval":
                self._pending[uid] = ev["id"]
                self.say(uid, f"Trợ lý muốn {KIND_LABEL.get(ev['kind'], ev['kind'])}:\n{ev['detail'][:1200]}\n\nTrả lời 'ok' để cho phép, 'không' để từ chối.")
            elif ev["type"] == "assistant" and ev["content"]:
                reply = ev["content"]
            elif ev["type"] == "error":
                error = ev["message"]
        self.say(uid, reply or (f"⚠ {error}" if error else "⚠ Trợ lý không trả lời được lần này. Hãy thử gửi lại."))
        fresh = [t["path"] for t in workfiles.tree(base) if not t["dir"] and before.get(t["path"]) != t["mtime"] and not t["path"].startswith("uploads/") and t["size"] > 0]
        if fresh:  # Zalo OA khong nhan file truc tiep qua API cs: bao ten file, nguoi dung mo trong giao dien Nestor
            self.say(uid, "📎 Tệp vừa tạo (mở trong mục Tệp của giao diện Nestor): " + ", ".join(fresh[:5]))

    def _notify(self, n: dict) -> None:
        if not self.status["running"]:
            return
        for uid in self.cfg.allowed_users:
            self.say(uid, f"🔔 {n['title']}\n{n['body']}")


channel = ZaloChannel()
