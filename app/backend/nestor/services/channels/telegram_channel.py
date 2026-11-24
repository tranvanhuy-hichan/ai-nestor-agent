"""Kenh Telegram (long polling, khong can cong mo ra ngoai): nhan tin -> agent -> tra loi, xin phep bang nut bam."""
import json
import logging
import re
import threading
import time
from dataclasses import dataclass
from hashlib import blake2s

import httpx

from nestor.core import config as cfgmod
from nestor.core.db import db
from nestor.services import chat_runner, knowledge, notifications, pairing, sessions, workfiles

from .telegram_markdown import formatted_chunks

log = logging.getLogger("telegram")
CHUNK = 4000
KIND_LABEL = {"exec": "chạy lệnh shell", "mcp": "gọi tool MCP", "file_read": "đọc file ngoài workspace", "file_write": "ghi file ngoài workspace"}

COMMANDS = {
    "new": "Mở hội thoại mới",
    "model": "Xem hoặc đổi model",
    "status": "Xem model và cài đặt hiện tại",
    "permission": "Chọn chế độ quyền",
    "effort": "Chọn mức suy luận",
    "docs": "Bật hoặc tắt hỏi từ tài liệu",
    "answer": "Trả lời câu hỏi của agent",
    "stop": "Dừng lượt đang chạy",
    "help": "Xem hướng dẫn",
    "id": "Xem ID Telegram",
    "pair": "Ghép đôi với Nestor",
}
COMMAND = re.compile(r"^/([a-z0-9_]+)(?:@([a-z0-9_]+))?(?:\s+(.*))?$", re.I | re.S)
APPROVAL = re.compile(r"ap:([a-f0-9]{32}):([01])")
CHOICE_LABELS = {
    "permission": {"guarded": "Hỏi trước", "readonly": "Chỉ đọc", "default": "Mặc định", "plan": "Lập kế hoạch"},
    "effort": {"auto": "Tự động", "low": "Thấp", "medium": "Trung bình", "high": "Cao", "thinking": "Suy nghĩ sâu"},
    "docs": {"on": "Bật", "off": "Tắt"},
}
CHOICE_TITLES = {"model": "Model", "permission": "Quyền", "effort": "Mức suy luận", "docs": "Hỏi từ tài liệu"}
CHOICE_DEFAULTS = {"permission": "guarded", "effort": "auto", "docs": "off"}
SHORTCUTS = {
    "model": "Model", "permission": "Quyền", "effort": "Mức suy luận", "docs": "Tài liệu",
    "new": "Hội thoại mới", "stop": "Dừng lượt",
}


def _button(label: str, data: str) -> dict:
    return {"text": label if len(label) <= 60 else label[:59] + "…", "callback_data": data}


def _choice_id(chat: int, group: str, value) -> str:
    key = json.dumps([chat, group, value], ensure_ascii=False).encode()
    return blake2s(key, digest_size=12).hexdigest()


def _menu_shortcuts(chat: int) -> list[list[dict]]:
    buttons = [_button(label, f"menu:{_choice_id(chat, 'menu', key)}") for key, label in SHORTCUTS.items()]
    return [buttons[i:i + 2] for i in range(0, len(buttons), 2)]


_PROVIDER_ICONS = (
    (("antigravity", "agy"), "🪐"),
    (("openrouter",), "🔀"),
    (("cloudflare",), "☁️"),
    (("groq",), "⚡"),
    (("cohere", "command-a", "command-r"), "🧩"),
    (("ollama", "11434"), "🦙"),
    (("google", "gemini", "generativelanguage"), "✨"),
    (("claude", "anthropic"), "🟠"),
    (("openai", "codex", "gpt"), "🟢"),
    (("deepseek",), "🐋"),
    (("qwen",), "🔮"),
    (("mistral",), "🌬️"),
    (("grok", "xai"), "✖️"),
)


def _provider_label(name: str, provider: cfgmod.ProviderCfg) -> str:
    # Inline button labels support Unicode rather than the web picker's SVG assets.
    cli = provider.cli if provider.type == "cli" else ""
    identity = f"{name} {cli} {provider.base_url}".lower()
    icon = next((icon for value in (identity, provider.model.lower()) for aliases, icon in _PROVIDER_ICONS
                 if any(alias in value for alias in aliases)), "🤖")
    label = f"{icon} {name}"
    return f"{label} · {provider.model}" if provider.model else label


def _choices(command: str, cfg, settings: dict):
    if command == "model":
        selected = settings.get("provider")
        if selected not in cfg.providers:
            selected = None
        items = [(name, _provider_label(name, provider)) for name, provider in cfg.providers.items()]
        if selected is None:
            selected = cfg.default_provider
        items.append((None, "Dùng model mặc định"))
        return selected, items
    values = CHOICE_LABELS[command]
    current = ("on" if settings.get("docs") else "off") if command == "docs" else settings.get(command, CHOICE_DEFAULTS[command])
    return current, list(values.items())


def _choice_picker(chat: int, command: str, cfg, settings: dict) -> tuple[str, list[list[dict]]]:
    current, items = _choices(command, cfg, settings)
    current_label = dict(items)[current] if command != "model" else current
    buttons = [[_button(("✓ " if value == current else "") + label, f"pick:{command}:{_choice_id(chat, command, value)}")]
               for value, label in items]
    return f"{CHOICE_TITLES[command]} đang dùng: {current_label}", buttons


def _save_choice(chat: int, command: str, value) -> None:
    key = "provider" if command == "model" else command
    _set_preference(chat, key, value == "on" if command == "docs" else value)


TURN_INSTRUCTIONS = (
    "Người dùng đang giao việc qua Telegram. Khi yêu cầu cần hành động và có công cụ phù hợp, "
    "hãy dùng cơ chế gọi công cụ được cung cấp ngay trong lượt này. Hệ thống sẽ tự gửi nút xin quyền khi cần. "
    "Không in cú pháp gọi công cụ hoặc yêu cầu người dùng nhắn lại để chạy công cụ. "
    "Nếu công cụ chưa có hoặc đã bị từ chối, giải thích ngắn gọn."
)


@dataclass
class PendingApproval:
    label: str
    message_id: int | None = None
    decision: bool | None = None


class TelegramAPIError(RuntimeError):
    pass


def _display_name(user: dict) -> str:
    return " ".join(filter(None, (user.get("first_name"), user.get("last_name")))).strip() or (
        f"@{user['username']}" if user.get("username") else ""
    )


def _preferences(chat: int) -> dict:
    with db() as c:
        row = c.execute("SELECT settings FROM telegram_chat_settings WHERE chat_id=?", (str(chat),)).fetchone()
    return json.loads(row["settings"]) if row else {}


def _set_preference(chat: int, key: str, value) -> None:
    with db() as c:
        c.execute("BEGIN IMMEDIATE")
        row = c.execute("SELECT settings FROM telegram_chat_settings WHERE chat_id=?", (str(chat),)).fetchone()
        settings = json.loads(row["settings"]) if row else {}
        settings[key] = value
        c.execute("INSERT OR REPLACE INTO telegram_chat_settings(chat_id,settings) VALUES(?,?)",
                  (str(chat), json.dumps(settings)))


def _link_get(chat_id: int) -> str | None:
    with db() as c:
        r = c.execute("SELECT session_id FROM channel_links WHERE channel='telegram' AND external_id=?", (str(chat_id),)).fetchone()
    return r["session_id"] if r and sessions.get(r["session_id"]) else None


def _link_set(chat_id: int, sid: str) -> None:
    with db() as c:
        c.execute("INSERT OR REPLACE INTO channel_links(channel,external_id,session_id) VALUES('telegram',?,?)", (str(chat_id), sid))


_SRC = re.compile(r"\s*\[\[src:[^|\]]+\|([^|\]]+)\|([^\]]+)\]\]")


def clean_reply(text: str) -> str:
    """Telegram khong ve duoc the nguon [[src:...]]: bo khoi cau va dua thanh dong 'Nguon' o cuoi."""
    found: dict[str, None] = {}
    for m in _SRC.finditer(text):
        found[f"{m.group(1).strip()} ({knowledge.display_source_location(m.group(2))})"] = None
    out = _SRC.sub("", text).strip()
    return out + ("\n\nNguồn: " + "; ".join(found)) if found else out


def _chunks(text: str) -> list[str]:
    size = CHUNK // 2  # an toàn cho cả ký tự chiếm hai đơn vị UTF-16
    return [text[i:i + size] for i in range(0, len(text), size)] or ["(không có nội dung)"]


class TelegramChannel:
    def __init__(self) -> None:
        self.cfg = cfgmod.TelegramCfg()
        self.stop_evt = threading.Event()
        self.thread: threading.Thread | None = None
        self.status = {"running": False, "error": "", "bot": ""}
        self._locks: dict[int, threading.Lock] = {}
        self._pending: dict[tuple[int, str], PendingApproval] = {}
        self._questions: dict[int, tuple[str, list[str]]] = {}
        self._approval_lock = threading.Lock()
        self._username = ""
        notifications.listeners.append(self._notify)

    # ---- vong doi
    def apply(self, cfg: cfgmod.TelegramCfg) -> None:
        if self.thread and (not cfg.enabled or cfg.token != self.cfg.token or cfg.api_base != self.cfg.api_base):
            self.stop_evt.set()
            self.thread = None
        self.cfg = cfg
        if cfg.enabled and cfg.token and (not self.thread or not self.thread.is_alive()):
            self.status = {"running": False, "error": "", "bot": ""}
            self.stop_evt = threading.Event()
            self.thread = threading.Thread(target=self._poll, args=(self.stop_evt,), daemon=True, name="telegram")
            self.thread.start()
        elif not cfg.enabled:
            self.status = {"running": False, "error": "", "bot": ""}

    def api(self, method: str, http_timeout: float = 40, **params) -> dict:
        try:
            response = httpx.post(f"{self.cfg.api_base}/bot{self.cfg.token}/{method}", json=params, timeout=http_timeout)
            data = response.json()
        except (httpx.HTTPError, ValueError):
            raise TelegramAPIError(f"{method}: không kết nối được Telegram") from None
        if not data.get("ok"):
            raise TelegramAPIError(f"{method}: {data.get('description', response.status_code)}")
        return data["result"]

    def _poll(self, stop: threading.Event) -> None:
        offset = 0
        try:
            me = self.api("getMe", http_timeout=15)
            if stop.is_set():
                return
            self._username = me.get("username", "")
            handle = f"@{self._username}" if self._username else ""
            name = _display_name(me)
            bot = f"{name} ({handle})" if name and handle and name != handle else name or handle
            self.status = {"running": True, "error": "", "bot": bot}
        except Exception as e:  # noqa: BLE001 - hien loi token len UI
            if not stop.is_set():
                self.status = {"running": False, "error": str(e)[:200], "bot": ""}
            return
        try:
            self.api("setMyCommands", http_timeout=15, commands=[
                {"command": command, "description": description} for command, description in COMMANDS.items()
            ])
        except TelegramAPIError as error:
            log.warning("Telegram commands: %s", error)
        while not stop.is_set():
            try:
                for u in self.api("getUpdates", http_timeout=40, offset=offset, timeout=20, allowed_updates=["message", "callback_query"]):
                    if stop.is_set():
                        return
                    offset = u["update_id"] + 1
                    threading.Thread(target=self._handle, args=(u,), daemon=True).start()
            except Exception as e:  # noqa: BLE001
                if not stop.is_set():
                    self.status["error"] = str(e)[:200]
                stop.wait(5)
            else:
                if not stop.is_set():
                    self.status["error"] = ""

    # ---- xu ly tin
    def _allowed(self, user_id: int) -> bool:
        return user_id in cfgmod.load().channels.telegram.allowed_users

    def _handle(self, u: dict) -> None:
        try:
            if "callback_query" in u:
                return self._on_callback(u["callback_query"])
            msg = u.get("message") or {}
            if not msg.get("from"):
                return
            uid, chat = msg["from"]["id"], msg["chat"]["id"]
            text = (msg.get("text") or msg.get("caption") or "").strip()
            match = COMMAND.fullmatch(text)
            command, addressed, argument = match.groups() if match else ("", None, None)
            command = command.lower()
            argument = (argument or "").strip()
            if addressed and addressed.casefold() != self._username.casefold():
                return
            if command == "id":
                return self._say(chat, f"ID Telegram của bạn: {uid}")
            if command == "pair":
                if self._allowed(uid):
                    return self._say(chat, "Tài khoản đã được cấp quyền.")
                if msg["chat"].get("type") != "private":
                    return self._say(chat, "Hãy gửi mã ghép đôi trong tin nhắn riêng với bot.")
                if pairing.submit("telegram", argument, uid, _display_name(msg["from"])):
                    return self._say(chat, "Đã gửi yêu cầu. Hãy duyệt trong giao diện web Nestor.")
                return self._say(chat, "Mã ghép đôi sai hoặc đã hết hạn. Tạo mã mới trong giao diện, mục Tích hợp > Kênh chat.")
            if not self._allowed(uid):
                return self._say(chat, "Bạn chưa được phép dùng agent này. Tạo mã ghép đôi trong giao diện web rồi gửi: /pair <mã>")
            if command and self._command(chat, msg, command, argument):
                return
            lock = self._locks.setdefault(chat, threading.Lock())
            if not lock.acquire(blocking=False):
                with self._approval_lock:
                    waiting = any(chat_id == chat for chat_id, _ in self._pending)
                    question = chat in self._questions
                if question:
                    return self._say(chat, "Dùng /answer để trả lời câu hỏi đang chờ.")
                return self._say(chat, "Hãy bấm nút Cho phép hoặc Từ chối trong tin xin quyền." if waiting
                                 else "Agent đang xử lý. Dùng /stop nếu muốn dừng lượt hiện tại.")
            try:
                self._run(chat, msg, text)
            finally:
                lock.release()
        except Exception as e:  # noqa: BLE001 - mot tin loi khong duoc lam chet luong polling
            log.warning("telegram handle: %s", e)
            try:
                chat = (u.get("message") or {}).get("chat", {}).get("id")
                if chat:
                    self.api("sendMessage", chat_id=chat, text=f"⚠ Lỗi khi xử lý: {str(e)[:300]}", http_timeout=15)
            except Exception:  # noqa: BLE001
                pass

    def _command(self, chat: int, msg: dict, command: str, argument: str) -> bool:
        cfg = cfgmod.load()
        settings = _preferences(chat)
        provider = settings.get("provider") or cfg.default_provider
        if provider not in cfg.providers:
            provider = cfg.default_provider
        keyboard = None
        if command in ("help", "start"):
            keyboard = _menu_shortcuts(chat)
            answer = ("Nhắn trực tiếp để giao việc. Khi cần quyền, bot sẽ hỏi bằng nút bấm.\n\n"
                      + "\n".join(f"/{name} — {description}" for name, description in COMMANDS.items()))
        elif command == "stop":
            sid = _link_get(chat)
            answer = "Đang dừng lượt hiện tại." if sid and chat_runner.stop(sid) else "Không có lượt nào đang chạy."
        elif command == "answer":
            with self._approval_lock:
                pending = self._questions.get(chat)
                if pending and argument:
                    qid, options = pending
                    value = argument
                    if len(argument) == 1 and argument in "12345678" and int(argument) <= len(options):
                        value = options[int(argument) - 1]
                    accepted = chat_runner.answer_question(qid, value)
                    self._questions.pop(chat, None)
                    answer = "Đã gửi câu trả lời." if accepted else "Câu hỏi đã hết hạn."
                else:
                    answer = "Dùng /answer <nội dung hoặc số lựa chọn>." if pending else "Không có câu hỏi đang chờ."
        elif command == "new":
            lock = self._locks.setdefault(chat, threading.Lock())
            if not lock.acquire(blocking=False):
                answer = "Agent đang xử lý. Dùng /stop rồi thử lại khi lượt kết thúc."
            else:
                try:
                    self._new_session(chat, msg)
                    answer = "Đã bắt đầu hội thoại mới."
                finally:
                    lock.release()
        elif command == "status":
            keyboard = _menu_shortcuts(chat)
            answer = (f"Model: {provider} ({cfg.providers[provider].model})\n"
                      f"Quyền: {settings.get('permission', 'guarded')}\n"
                      f"Mức suy luận: {settings.get('effort', 'auto')}\n"
                      f"Hỏi từ tài liệu: {'bật' if settings.get('docs') else 'tắt'}")
        elif command == "model":
            names = list(cfg.providers)
            if not argument:
                answer, keyboard = _choice_picker(chat, command, cfg, settings)
            elif argument == "default":
                _save_choice(chat, command, None)
                answer = f"Đã chọn model mặc định: {cfg.default_provider}."
            else:
                selected = argument
                if selected not in names and selected.isdecimal() and len(selected) <= 6 and 1 <= int(selected) <= len(names):
                    selected = names[int(selected) - 1]
                if selected in names:
                    _save_choice(chat, command, selected)
                    answer = f"Lượt tiếp theo dùng model {selected} ({cfg.providers[selected].model})."
                else:
                    answer = "Không có model này. Gõ /model để xem danh sách."
        elif command in CHOICE_LABELS:
            value = argument.lower()
            if value not in CHOICE_LABELS[command]:
                answer, keyboard = _choice_picker(chat, command, cfg, settings)
            else:
                _save_choice(chat, command, value)
                answer = f"Đã lưu cho lượt tiếp theo: {CHOICE_LABELS[command][value]}."
        else:
            return False  # các lệnh skill vẫn được xử lý như tin nhắn chat
        self._say(chat, answer, keyboard=keyboard)
        return True

    def _new_session(self, chat: int, msg: dict) -> str:
        label = msg["chat"].get("title") or _display_name(msg["from"])
        sid = sessions.create(f"Telegram · {label}"[:100] if label else "Telegram", source="telegram")
        _link_set(chat, sid)
        return sid

    def _say(self, chat: int, text: str, *, markdown: bool = False, keyboard: list[list[dict]] | None = None) -> None:
        text = clean_reply(text)
        try:
            parts = formatted_chunks(text, CHUNK) if markdown else []
        except (ValueError, RecursionError):
            parts = []
        if not parts:
            parts = [(None, part) for part in _chunks(text)]
        for index, (formatted, plain) in enumerate(parts):
            markup = {"reply_markup": {"inline_keyboard": keyboard}} if keyboard and index == len(parts) - 1 else {}
            for attempt in range(3):
                try:
                    if formatted is not None:
                        try:
                            self.api("sendMessage", chat_id=chat, text=formatted, parse_mode="HTML", **markup)
                            break
                        except TelegramAPIError as error:
                            if "entit" not in str(error).lower():
                                raise
                            formatted = None
                    self.api("sendMessage", chat_id=chat, text=plain, **markup)
                    break
                except TelegramAPIError as error:
                    log.warning("telegram sendMessage (lan %d): %s", attempt + 1, error)
                    if attempt == 2:
                        raise
                    time.sleep(2 * (attempt + 1))

    def _ask_approval(self, chat: int, event: dict) -> None:
        aid = event["id"]
        label = KIND_LABEL.get(event["kind"], event["kind"])
        pending = PendingApproval(label)
        with self._approval_lock:
            self._pending[chat, aid] = pending
        try:
            message = self.api(
                "sendMessage", chat_id=chat, text=f"Agent muốn {label}:\n{event['detail'][:1800]}",
                reply_markup={"inline_keyboard": [[
                    {"text": "✅ Cho phép", "callback_data": f"ap:{aid}:1"},
                    {"text": "❌ Từ chối", "callback_data": f"ap:{aid}:0"},
                ]]},
            )
            pending.message_id = message["message_id"]
        except TelegramAPIError:
            chat_runner.resolve_approval(aid, False)
            raise

    def _finish_approval(self, chat: int, aid: str, ok: bool) -> None:
        with self._approval_lock:
            pending = self._pending.pop((chat, aid), None)
        if not pending or pending.message_id is None:
            return
        status = "✅ Đã cho phép" if ok else "❌ Đã từ chối" if pending.decision is False else "⌛ Đã đóng yêu cầu"
        try:
            self.api("editMessageText", chat_id=chat, message_id=pending.message_id,
                     text=f"{status} · {pending.label}", reply_markup={"inline_keyboard": []})
        except TelegramAPIError as error:
            log.warning("Telegram approval message: %s", error)

    def _download(self, sid: str, msg: dict) -> list[str]:
        file_id = name = None
        if msg.get("photo"):
            file_id, name = msg["photo"][-1]["file_id"], f"anh_{msg['message_id']}.jpg"
        elif msg.get("document"):
            file_id, name = msg["document"]["file_id"], msg["document"].get("file_name") or f"tep_{msg['message_id']}"
        if not file_id:
            return []
        info = self.api("getFile", file_id=file_id)
        if info.get("file_size", 0) > workfiles.MAX_UPLOAD:
            return []
        try:
            download = httpx.get(f"{self.cfg.api_base}/file/bot{self.cfg.token}/{info['file_path']}", timeout=60)
            download.raise_for_status()
            data = download.content
        except httpx.HTTPError:
            raise TelegramAPIError("Không tải được tệp từ Telegram.") from None
        if len(data) > workfiles.MAX_UPLOAD:
            return []
        dest = workfiles.session_dir(cfgmod.load(), sid) / "uploads" / "".join(ch if ch.isalnum() or ch in "._- " else "_" for ch in name)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        return [dest.relative_to(workfiles.session_dir(cfgmod.load(), sid)).as_posix()]

    def _run(self, chat: int, msg: dict, text: str) -> None:
        sid = _link_get(chat) or self._new_session(chat, msg)
        attachments = self._download(sid, msg)
        text = text or "(người dùng gửi tệp đính kèm)"
        typing_stop = threading.Event()

        def keep_typing() -> None:
            while not typing_stop.is_set():
                try:
                    self.api("sendChatAction", chat_id=chat, action="typing", http_timeout=10)
                except TelegramAPIError:
                    pass
                typing_stop.wait(4)

        before = {t["path"]: t["mtime"] for t in workfiles.tree(workfiles.session_dir(cfgmod.load(), sid)) if not t["dir"]}
        settings = _preferences(chat)
        cfg = cfgmod.load()
        provider = settings.get("provider")
        if provider not in cfg.providers:
            provider = cfg.default_provider
        effort = settings.get("effort", "auto")
        threading.Thread(target=keep_typing, daemon=True).start()
        reply, error, stopped = "", "", False
        run = None
        try:
            for ev in chat_runner.stream_chat(
                sid, text, provider, source="telegram", attachments=attachments,
                permission=settings.get("permission", "guarded"), effort=None if effort == "auto" else effort,
                docs=settings.get("docs", False), system_extra=TURN_INSTRUCTIONS,
            ):
                if ev["type"] == "session" and ev.get("run_id"):
                    run = chat_runner.lookup_run(sid, ev["run_id"])
                elif ev["type"] == "done" and run:
                    stopped = run.cancel.is_set()
                elif ev["type"] == "approval":
                    self._ask_approval(chat, ev)
                elif ev["type"] == "approval_done":
                    self._finish_approval(chat, ev["id"], ev["ok"])
                elif ev["type"] == "assistant" and ev["content"] and not ev.get("has_tool_calls"):
                    reply = ev["content"]
                elif ev["type"] == "question":
                    options = ev.get("options", [])
                    with self._approval_lock:
                        self._questions[chat] = (ev["id"], options)
                    lines = [ev["question"]]
                    lines.extend(f"{i}. {item['question']} " + " / ".join(item.get("options", []))
                                 for i, item in enumerate(ev.get("form") or [], 1))
                    lines.append("Bấm một lựa chọn hoặc dùng /answer để nhập câu trả lời." if options
                                 else "Dùng /answer để nhập câu trả lời.")
                    keyboard = [[_button(option, f"reply:{_choice_id(chat, ev['id'], index)}")]
                                for index, option in enumerate(options)]
                    self._say(chat, "\n".join(lines), markdown=True, keyboard=keyboard)
                elif ev["type"] == "question_done":
                    with self._approval_lock:
                        self._questions.pop(chat, None)
                elif ev["type"] == "error":
                    error = ev["message"]
                elif ev["type"] == "notice" and ev.get("message") == "Đã dừng":
                    stopped = True
        finally:
            typing_stop.set()
            with self._approval_lock:
                self._questions.pop(chat, None)
                remaining = [aid for chat_id, aid in self._pending if chat_id == chat]
            for aid in remaining:
                self._finish_approval(chat, aid, False)
        if reply and not stopped:
            self._say(chat, reply, markdown=True)
        if error and not stopped:
            self._say(chat, f"⚠ {error}")
        elif stopped:
            self._say(chat, "Đã dừng lượt hiện tại.")
        elif not reply:
            self._say(chat, "⚠ Agent chưa có câu trả lời. Hãy thử lại hoặc dùng /model để chọn model khác.")
        base = workfiles.session_dir(cfgmod.load(), sid)
        fresh = [t for t in workfiles.tree(base) if not t["dir"] and before.get(t["path"]) != t["mtime"]
                 and not t["path"].startswith("uploads/") and 0 < t["size"] <= 10 * 1024 * 1024]
        for t in fresh[:3]:  # gui toi da 3 file agent vua tao/sua
            self._send_file(chat, base / t["path"])

    def _send_file(self, chat: int, path) -> None:
        try:
            response = httpx.post(f"{self.cfg.api_base}/bot{self.cfg.token}/sendDocument", data={"chat_id": chat},
                                  files={"document": (path.name, path.read_bytes())}, timeout=60)
            response.raise_for_status()
        except httpx.HTTPError:
            raise TelegramAPIError("Không gửi được tệp qua Telegram.") from None

    def _choice_callback(self, cq: dict, message: dict, chat: int, data: str) -> bool:
        def acknowledge(text: str = "") -> None:
            self.api("answerCallbackQuery", callback_query_id=cq["id"], text=text)

        def edit(method: str, **params) -> None:
            try:
                self.api(method, chat_id=chat, message_id=message["message_id"], **params)
            except TelegramAPIError as error:
                if "message is not modified" not in str(error).lower():
                    log.warning("Telegram button update: %s", error)

        kind, _, payload = data.partition(":")
        if kind == "menu":
            command = next((key for key in SHORTCUTS if _choice_id(chat, "menu", key) == payload), None)
            if command:
                acknowledge()
                self._command(chat, {**message, "from": cq["from"]}, command, "")
            else:
                acknowledge("Nút này đã hết hạn.")
        elif kind == "pick":
            command, _, ident = payload.partition(":")
            if command not in CHOICE_TITLES:
                acknowledge("Nút này đã hết hạn.")
                return True
            cfg = cfgmod.load()
            settings = _preferences(chat)
            _, items = _choices(command, cfg, settings)
            for value, _ in items:
                if _choice_id(chat, command, value) == ident:
                    _save_choice(chat, command, value)
                    text, keyboard = _choice_picker(chat, command, cfg, _preferences(chat))
                    acknowledge("Đã lưu cho lượt tiếp theo.")
                    edit("editMessageText", text=text, reply_markup={"inline_keyboard": keyboard})
                    return True
            acknowledge("Tùy chọn này không còn khả dụng. Hãy mở lại menu.")
        elif kind == "reply":
            accepted = False
            with self._approval_lock:
                if pending := self._questions.get(chat):
                    qid, options = pending
                    for index, option in enumerate(options):
                        if _choice_id(chat, qid, index) == payload:
                            accepted = chat_runner.answer_question(qid, option)
                            self._questions.pop(chat, None)
                            break
            acknowledge("Đã gửi câu trả lời." if accepted else "Câu hỏi đã hết hạn.")
            edit("editMessageReplyMarkup", reply_markup={"inline_keyboard": []})
        else:
            return False
        return True

    def _on_callback(self, cq: dict) -> None:
        if not self._allowed(cq["from"]["id"]):
            return self.api("answerCallbackQuery", callback_query_id=cq["id"], text="Bạn không có quyền.")
        data = cq.get("data", "")
        match = APPROVAL.fullmatch(data)
        m = cq.get("message") or {}
        chat = (m.get("chat") or {}).get("id")
        if chat is not None and m.get("message_id") and self._choice_callback(cq, m, chat, data):
            return
        done = False
        if match and chat is not None:
            aid, ok = match.groups()
            with self._approval_lock:
                pending = self._pending.get((chat, aid))
                if pending and pending.decision is None and pending.message_id in (None, m.get("message_id")):
                    done = chat_runner.resolve_approval(aid, ok == "1")
                    if done:
                        pending.decision = ok == "1"
        self.api("answerCallbackQuery", callback_query_id=cq["id"], text="Đã ghi nhận" if done else "Yêu cầu đã hết hạn")

    # ---- thong bao chu dong (heartbeat, automation)
    def _notify(self, n: dict) -> None:
        if not self.status["running"]:
            return
        for uid in self.cfg.allowed_users:
            self._say(uid, f"🔔 {n['title']}\n{n['body']}")


channel = TelegramChannel()
