"""Kenh chat (Telegram, Zalo), heartbeat va dang nhap giao dien."""
import httpx
from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel

from ..core import config as cfgmod
from ..services import auth, heartbeat, pairing
from ..services.telegram_channel import channel
from ..services.zalo_channel import channel as zalo
from ..services.zalo_channel import verify as zalo_verify

router = APIRouter()


@router.get("/channels/pairing")
def pairing_requests():
    return pairing.pending()


class PairDecision(BaseModel):
    approve: bool


@router.post("/channels/pairing/{key}")
def decide_pairing(key: str, body: PairDecision):
    try:
        request = pairing.decide(key, body.approve)
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc
    if request is None:
        raise HTTPException(404, "Yêu cầu đã hết hạn hoặc đã được xử lý")
    if body.approve:
        cfg = cfgmod.load().channels
        if request["channel"] == "telegram":
            channel.apply(cfg.telegram)
        else:
            zalo.apply(cfg.zalo)
    return {"ok": True}


# ---------- Telegram
@router.get("/channels")
def channels_status():
    cfg = cfgmod.load().channels.telegram
    return {"telegram": {**channel.status, "enabled": cfg.enabled, "has_token": bool(cfg.token), "allowed_users": cfg.allowed_users, "api_base": cfg.api_base},
            "zalo": _zalo_public(cfgmod.load().channels.zalo)}


class TgConfig(BaseModel):
    enabled: bool
    token: str = ""  # de trong = giu token cu
    api_base: str = "https://api.telegram.org"


@router.put("/channels/telegram")
def channels_save(b: TgConfig):
    cfg = cfgmod.load()
    tg = cfg.channels.telegram
    previous = (tg.token, tg.api_base)
    tg.enabled, tg.api_base = b.enabled, b.api_base.rstrip("/")
    if b.token and b.token != cfgmod.MASK:
        tg.token = b.token.strip()
    if tg.enabled and not tg.token:
        raise HTTPException(400, "cần nhập token bot")
    cfgmod.save(cfg)
    if not tg.enabled or previous != (tg.token, tg.api_base):
        pairing.invalidate("telegram")
    channel.apply(tg)
    return {"ok": True}


@router.post("/channels/telegram/pair-code")
def pair_code():
    return {"code": pairing.invite("telegram"), "expires_in": pairing.CODE_TTL}


class RemoveUser(BaseModel):
    user_id: int


@router.post("/channels/telegram/remove-user")
def remove_user(b: RemoveUser):
    cfg = cfgmod.load()
    cfg.channels.telegram.allowed_users = [u for u in cfg.channels.telegram.allowed_users if u != b.user_id]
    cfgmod.save(cfg)
    channel.apply(cfg.channels.telegram)
    return {"ok": True}


class TgTest(BaseModel):
    token: str = ""
    api_base: str = "https://api.telegram.org"


@router.post("/channels/telegram/test")
def channels_test(b: TgTest):
    token = b.token if b.token and b.token != cfgmod.MASK else cfgmod.load().channels.telegram.token
    try:
        r = httpx.post(f"{b.api_base.rstrip('/')}/bot{token}/getMe", timeout=15).json()
    except (httpx.HTTPError, ValueError):
        return {"ok": False, "error": "không kết nối được Telegram"}
    return {"ok": True, "bot": "@" + r["result"].get("username", "")} if r.get("ok") else {"ok": False, "error": r.get("description", "token không hợp lệ")}


# ---------- Heartbeat
@router.get("/heartbeat")
def hb_status():
    return heartbeat.status()


class HbBody(BaseModel):
    enabled: bool
    interval_minutes: int
    provider: str | None = None


@router.put("/heartbeat")
def hb_save(b: HbBody):
    cfg = cfgmod.load()
    cfg.heartbeat = cfgmod.HeartbeatCfg(**b.model_dump())
    cfgmod.save(cfg)
    f = cfg.workspace_path() / "HEARTBEAT.md"
    if b.enabled and not f.exists():
        f.write_text(heartbeat.DEFAULT_FILE)
    return heartbeat.status()


@router.post("/heartbeat/run")
def hb_run():
    import threading
    threading.Thread(target=heartbeat.run_once, daemon=True).start()
    return {"ok": True}


# ---------- Dang nhap
class Login(BaseModel):
    password: str


@router.get("/auth/status")
def auth_status(request: Request):
    cfg = cfgmod.load()
    return {"required": bool(cfg.auth.password_hash), "authenticated": not cfg.auth.password_hash or auth.verify_token(request.cookies.get(auth.COOKIE))}


@router.post("/auth/login")
def auth_login(b: Login, request: Request, response: Response):
    ip = request.client.host if request.client else "?"
    if auth.throttled(ip):
        raise HTTPException(429, "thử sai quá nhiều lần, vui lòng đợi vài phút")
    if not auth.check_password(cfgmod.load(), b.password):
        auth.record_failure(ip)
        raise HTTPException(401, "sai mật khẩu")
    response.set_cookie(auth.COOKIE, auth.make_token(), max_age=auth.TTL, httponly=True, samesite="strict", secure=request.url.scheme == "https")
    return {"ok": True}


@router.post("/auth/logout")
def auth_logout(response: Response):
    response.delete_cookie(auth.COOKIE)
    return {"ok": True}


class SetPassword(BaseModel):
    current: str = ""
    new: str = ""


@router.post("/auth/password")
def auth_password(b: SetPassword, request: Request):
    cfg = cfgmod.load()
    if cfg.auth.password_hash and not auth.check_password(cfg, b.current):
        raise HTTPException(403, "mật khẩu hiện tại không đúng")
    if b.new and len(b.new) < 8:
        raise HTTPException(400, "mật khẩu mới cần ít nhất 8 ký tự")
    auth.set_password(cfg, b.new)
    cfgmod.save(cfg)
    return {"ok": True, "required": bool(b.new)}


# ---------- Zalo OA
def _zalo_public(z: cfgmod.ZaloCfg) -> dict:
    return {**zalo.status, "enabled": z.enabled, "oa_id": z.oa_id, "app_id": z.app_id, "allowed_users": z.allowed_users,
            "has_app_secret": bool(z.app_secret), "has_access_token": bool(z.access_token), "has_refresh_token": bool(z.refresh_token), "has_webhook_secret": bool(z.webhook_secret),
            "webhook_path": "/api/channels/zalo/webhook"}


@router.get("/channels/zalo")
def zalo_status():
    return _zalo_public(cfgmod.load().channels.zalo)


class ZaloConfig(BaseModel):
    enabled: bool
    oa_id: str = ""
    app_id: str = ""
    app_secret: str = ""  # de trong hoac '***' = giu gia tri cu (ap dung cho moi truong bi mat)
    access_token: str = ""
    refresh_token: str = ""
    webhook_secret: str = ""


@router.put("/channels/zalo")
def zalo_save(b: ZaloConfig):
    cfg = cfgmod.load()
    z = cfg.channels.zalo
    previous = (z.oa_id, z.app_id, z.webhook_secret)
    z.enabled, z.oa_id, z.app_id = b.enabled, b.oa_id.strip(), b.app_id.strip()
    for k in cfgmod.ZALO_SECRETS:
        v = getattr(b, k)
        if v and v != cfgmod.MASK:
            setattr(z, k, v.strip())
    if z.enabled and not (z.access_token or z.refresh_token):
        raise HTTPException(400, "cần nhập access token (hoặc refresh token) của Zalo OA")
    if z.enabled and not z.webhook_secret:
        raise HTTPException(400, "cần đặt webhook secret để xác thực tin nhắn từ Zalo")
    cfgmod.save(cfg)
    if not z.enabled or previous != (z.oa_id, z.app_id, z.webhook_secret):
        pairing.invalidate("zalo")
    zalo.apply(z)
    return _zalo_public(z)


@router.post("/channels/zalo/pair-code")
def zalo_pair_code():
    return {"code": pairing.invite("zalo"), "expires_in": pairing.CODE_TTL}


class ZaloRemove(BaseModel):
    user_id: str


@router.post("/channels/zalo/remove-user")
def zalo_remove_user(b: ZaloRemove):
    cfg = cfgmod.load()
    cfg.channels.zalo.allowed_users = [u for u in cfg.channels.zalo.allowed_users if u != b.user_id]
    cfgmod.save(cfg)
    zalo.apply(cfg.channels.zalo)
    return {"ok": True}


@router.post("/channels/zalo/webhook")
async def zalo_webhook(request: Request, secret: str = ""):
    """Zalo goi vao day (qua tunnel/domain cong khai). Xac thuc bang X-ZEvent-Signature hoac ?secret=; xu ly nen, tra 200 ngay."""
    import json
    import threading
    body = await request.body()
    try:
        event = json.loads(body)
    except ValueError:
        event = None
    z = cfgmod.load().channels.zalo
    ts = str(event.get("timestamp", "")) if isinstance(event, dict) else ""
    if not z.enabled or not zalo_verify(z, body, request.headers.get("x-zevent-signature", ""), ts, secret):
        raise HTTPException(403, "chữ ký không hợp lệ")
    if not isinstance(event, dict):
        raise HTTPException(400, "payload không phải JSON")
    zalo.apply(z)
    threading.Thread(target=zalo.handle_event, args=(event,), daemon=True).start()
    return {"ok": True}
