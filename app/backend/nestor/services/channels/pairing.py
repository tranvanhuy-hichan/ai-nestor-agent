"""One-time channel invitations followed by explicit web approval."""
import secrets
import threading
import time
from typing import Literal

from nestor.core import config

Channel = Literal["telegram", "zalo"]
CODE_TTL = 600
REQUEST_TTL = 900
_lock = threading.Lock()
_codes: dict[tuple[Channel, str], float] = {}
_pending: dict[str, dict] = {}


def _prune(now: float):
    for key, expiry in list(_codes.items()):
        if expiry <= now:
            del _codes[key]
    for key, request in list(_pending.items()):
        if request["expires"] <= now:
            del _pending[key]


def invalidate(channel: Channel) -> None:
    with _lock:
        for key in list(_codes):
            if key[0] == channel:
                del _codes[key]
        for key, request in list(_pending.items()):
            if request["channel"] == channel:
                del _pending[key]


def invite(channel: Channel) -> str:
    with _lock:
        now = time.time()
        _prune(now)
        for key in list(_codes):
            if key[0] == channel:
                del _codes[key]
        code = secrets.token_urlsafe(12)
        _codes[channel, code] = now + CODE_TTL
        return code


def submit(channel: Channel, code: str, user_id: int | str, name: str = "") -> bool:
    with _lock:
        now = time.time()
        _prune(now)
        if not _codes.pop((channel, code), None):
            return False
        for key, request in list(_pending.items()):
            if request["channel"] == channel and request["user_id"] == user_id:
                del _pending[key]
        key = secrets.token_urlsafe(12)
        _pending[key] = {
            "id": key, "channel": channel, "user_id": user_id, "name": name[:100],
            "expires": now + REQUEST_TTL,
        }
        return True


def pending() -> list[dict]:
    with _lock:
        _prune(time.time())
        return list(_pending.values())


def decide(key: str, approve: bool) -> dict | None:
    with _lock:
        _prune(time.time())
        request = _pending.get(key)
        if request is None:
            return None
        if approve:
            cfg = config.load()
            channel = getattr(cfg.channels, request["channel"])
            if not channel.enabled:
                raise ValueError("Kênh đã tắt")
            if request["user_id"] not in channel.allowed_users:
                channel.allowed_users.append(request["user_id"])
                config.save(cfg)
        del _pending[key]
        return request
