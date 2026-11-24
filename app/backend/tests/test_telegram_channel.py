import threading

from nestor.core import config
from nestor.services import agent, chat_runner, notifications, sessions
from nestor.services.channels.telegram_channel import TelegramAPIError, TelegramChannel, _link_get, _preferences
from nestor.services.channels.telegram_markdown import formatted_chunks


def _message(text, chat=25, user=11):
    return {"message": {"from": {"id": user, "first_name": "Huy", "last_name": "Trần"},
                        "chat": {"id": chat, "type": "private"}, "text": text}}


def _channel(monkeypatch):
    monkeypatch.setattr(notifications, "listeners", [])
    cfg = config.load()
    cfg.channels.telegram.allowed_users = [11]
    config.save(cfg)
    telegram = TelegramChannel()
    calls = []

    def api(method, **params):
        calls.append((method, params))
        return {"message_id": len(calls)}

    monkeypatch.setattr(telegram, "api", api)
    return telegram, calls


def test_commands_store_model_and_other_settings_and_start_named_thread(tmp_env, monkeypatch):
    telegram, calls = _channel(monkeypatch)
    cfg = config.load()
    cfg.providers["second"] = config.ProviderCfg(model="vision")
    config.save(cfg)
    telegram._username = "sample_bot"
    telegram._handle(_message("/model@other_bot second"))
    assert not calls
    telegram._handle(_message("/model@sample_bot 2"))
    telegram._handle(_message("/permission readonly"))
    telegram._handle(_message("/effort high"))
    telegram._handle(_message("/docs on"))
    assert _preferences(25) == {"provider": "second", "permission": "readonly", "effort": "high", "docs": True}
    telegram._handle(_message("/new"))
    sid = _link_get(25)
    assert sessions.get(sid)["title"] == "Telegram · Huy Trần"
    telegram._handle(_message("/new"))
    assert _link_get(25) != sid and sessions.get(sid)
    telegram._handle(_message("/status"))
    assert "second (vision)" in calls[-1][1]["text"]
    telegram._handle(_message("/model default", user=99))
    assert _preferences(25)["provider"] == "second"
    assert "chưa được phép" in calls[-1][1]["text"]


def test_tool_format_retry_runs_actual_tool_and_compacts_approval(tmp_env, monkeypatch):
    telegram, calls = _channel(monkeypatch)
    seen = []
    approval_shown = threading.Event()
    original_api = telegram.api

    def api(method, **params):
        result = original_api(method, **params)
        if method == "sendMessage" and params.get("reply_markup"):
            approval_shown.set()
            return {"message_id": 99}
        return result

    monkeypatch.setattr(telegram, "api", api)

    class Provider:
        def stream(self, messages, tools, **kwargs):
            seen.append(messages)
            if len(seen) == 1:
                assert "nút xin quyền" in messages[0]["content"]
                assert any(tool["name"] == "write" for tool in tools)
                text = '<tool_call>{"name":"write","arguments":{"path":"ignored.txt"}}</tool_call>'
                result = []
            elif len(seen) == 2:
                assert "Không in cú pháp" in messages[-1]["content"]
                text = "Đang gọi công cụ"
                result = [{"id": "call1", "name": "write", "args": {"path": "done.txt", "content": "ok"}}]
            else:
                assert messages[-1]["role"] == "tool"
                assert "da ghi" in messages[-1]["content"]
                text, result = "**Hoàn tất** & đã lưu.", []
            yield {"type": "final", "content": text, "tool_calls": result, "usage": {"prompt": 1, "completion": 1}}

    monkeypatch.setattr(agent, "make_provider", lambda cfg: Provider())
    monkeypatch.setattr(telegram, "_send_file", lambda *args: None)
    worker = threading.Thread(target=telegram._handle, args=(_message("Hãy tạo tệp."),), daemon=True)
    worker.start()
    assert approval_shown.wait(5)
    approval = next(params for method, params in calls if method == "sendMessage" and params.get("reply_markup"))
    approval_data = approval["reply_markup"]["inline_keyboard"][0][0]["callback_data"]
    callback = {"from": {"id": 11}, "id": "callback", "data": approval_data,
                "message": {"chat": {"id": 26}, "message_id": 99}}
    telegram._on_callback(callback)
    assert calls[-1][1]["text"] == "Yêu cầu đã hết hạn"
    callback["message"]["chat"]["id"] = 25
    telegram._on_callback(callback)
    worker.join(5)
    assert not worker.is_alive()
    assert len(seen) == 3
    assert all("<tool_call>" not in params.get("text", "") and "Đang gọi công cụ" not in params.get("text", "")
               for _, params in calls)
    edited = next(params for method, params in calls if method == "editMessageText")
    assert edited["reply_markup"] == {"inline_keyboard": []}
    assert edited["text"].startswith("✅ Đã cho phép") and "done.txt" not in edited["text"]
    assert any(params.get("parse_mode") == "HTML" and "<b>Hoàn tất</b> &amp;" in params["text"] for _, params in calls)
    sid = _link_get(25)
    assert (config.load().workspace_path() / "sessions" / sid / "done.txt").read_text() == "ok"
    assert not telegram._pending


def test_markdown_is_balanced_when_split_and_plain_when_rejected(tmp_env, monkeypatch):
    telegram, calls = _channel(monkeypatch)
    parts = formatted_chunks("# Tiêu đề\n\n**đậm** và [link](https://example.org)\n\n```text\n" + "😀" * 2100 + "\n```")
    assert len(parts) >= 2
    assert "<b>Tiêu đề</b>" in parts[0][0] and '<a href="https://example.org">' in parts[0][0]
    assert sum(plain.count("😀") for _, plain in parts) == 2100
    for html, plain in parts:
        assert len(plain.encode("utf-16-le")) // 2 <= 4000
        assert html.count("<pre>") == html.count("</pre>")
        assert html.count('<code class="language-text">') == html.count("</code>")

    original_api = telegram.api

    def reject_format(method, **params):
        if params.get("parse_mode"):
            raise TelegramAPIError("sendMessage: can't parse entities")
        return original_api(method, **params)

    monkeypatch.setattr(telegram, "api", reject_format)
    telegram._say(25, "**Đậm** & chữ thường", markdown=True)
    assert calls == [("sendMessage", {"chat_id": 25, "text": "Đậm & chữ thường\n\n"})]


def test_stale_approval_is_shortened_and_answer_uses_choice(tmp_env, monkeypatch):
    telegram, calls = _channel(monkeypatch)
    aid = "e" * 32
    telegram._ask_approval(25, {"id": aid, "kind": "exec", "detail": "Long details"})
    telegram._finish_approval(25, aid, False)
    assert calls[-1][0] == "editMessageText"
    assert calls[-1][1]["text"] == "⌛ Đã đóng yêu cầu · chạy lệnh shell"
    assert calls[-1][1]["reply_markup"] == {"inline_keyboard": []}
    answers = []
    monkeypatch.setattr(chat_runner, "answer_question", lambda qid, answer: answers.append((qid, answer)) or True)
    telegram._questions[25] = ("q1", ["Một", "Hai"])
    telegram._handle(_message("/answer 2"))
    assert answers == [("q1", "Hai")] and not telegram._questions
