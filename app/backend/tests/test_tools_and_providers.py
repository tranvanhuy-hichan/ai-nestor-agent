import json
from pathlib import Path

import pytest

from nestor.core.config import ProviderCfg
from nestor.services import providers, tools


def ctx(tmp_path, approver=lambda k, d: False):
    ws = tmp_path / "ws"
    (ws / "s1").mkdir(parents=True)
    return tools.ToolContext(workspace=ws, cwd=ws / "s1", approver=approver, confirm_exec=True)


def test_relative_paths_live_in_session_dir_and_outside_needs_approval(tmp_path):
    asked = []
    c = ctx(tmp_path, lambda k, d: asked.append((k, d)) or False)
    assert tools.call(c, "write", {"path": "a.txt", "content": "hi"})[1]
    assert (c.cwd / "a.txt").read_text() == "hi" and not asked
    out, ok = tools.call(c, "read", {"path": "/etc/hostname"})
    assert not ok and asked and asked[0][0] == "file_read"


def test_exec_denied_does_not_run(tmp_path):
    c = ctx(tmp_path)
    out, ok = tools.call(c, "exec", {"command": "touch should-not-exist"})
    assert "KHÔNG THỰC HIỆN" in out and not (c.cwd / "should-not-exist").exists()


def test_exec_runs_in_session_dir_when_approved(tmp_path):
    c = ctx(tmp_path, lambda k, d: True)
    out, ok = tools.call(c, "exec", {"command": "pwd && echo x > f.txt"})
    assert ok and str(c.cwd) in out and (c.cwd / "f.txt").exists()


def test_edit_requires_unique_match(tmp_path):
    c = ctx(tmp_path, lambda k, d: True)
    (c.cwd / "f.txt").write_text("a a b")
    assert not tools.call(c, "edit", {"path": "f.txt", "old": "a", "new": "z"})[1]  # xuat hien 2 lan
    assert tools.call(c, "edit", {"path": "f.txt", "old": "b", "new": "z"})[1] and (c.cwd / "f.txt").read_text() == "a a z"


@pytest.mark.parametrize("url", ["http://127.0.0.1:8787/api", "http://localhost/x", "http://169.254.169.254/latest", "http://10.0.0.1/", "file:///etc/passwd", "ftp://x/y"])
def test_ssrf_blocked(url):
    with pytest.raises((PermissionError, ValueError, OSError)):
        tools._check_url(url)


def test_disabled_and_unknown_tools(tmp_path):
    c = ctx(tmp_path)
    c.enabled = {"read": False}
    assert not tools.call(c, "read", {"path": "x"})[1] and not tools.call(c, "nope", {})[1]
    assert "read" not in [s["name"] for s in tools.schemas(c)]


def test_deferred_tools_respect_scope_and_require_original_approval(tmp_path):
    from nestor.core.config import ToolPolicy

    c = ctx(tmp_path)
    ran = []
    visible = "crm__write_record"
    hidden = "crm__read_secret"
    c.extra = {name: tools.ToolDef(name, "CRM records", {}, lambda ctx: ran.append(True), "mcp")
               for name in (visible, hidden)}
    c.enabled[hidden] = False
    c.policies[visible] = ToolPolicy(approval="ask")
    tools.configure_discovery(c)

    assert visible not in {item["name"] for item in tools.schemas(c)}
    found = tools.tool_search(c, "crm")
    assert visible in found and hidden not in found
    assert tools.call(c, "tool_describe", {"names": [visible, hidden]})[1]
    assert {visible, "tool_search"} <= {item["name"] for item in tools.schemas(c)}
    assert hidden not in {item["name"] for item in tools.schemas(c)}
    assert not tools.call(c, visible, {})[1] and not ran


class FakeStream:
    def __init__(self, lines, status=200):
        self.lines, self.status_code, self.text = lines, status, "err"

    def __enter__(self): return self
    def __exit__(self, *a): return False
    def read(self): pass
    def iter_lines(self): return iter(self.lines)


def sse(*chunks):
    return [f"data: {json.dumps(c)}" for c in chunks] + ["data: [DONE]"]


def run(monkeypatch, lines, **kw):
    monkeypatch.setattr(providers.httpx, "stream", lambda *a, **k: FakeStream(lines, **kw))
    cfg = ProviderCfg(base_url="http://x/v1", model="m")
    return list(providers.OpenAICompat(cfg).stream([{"role": "user", "content": "hi"}], []))


def tc(i, **fn):
    return {"choices": [{"delta": {"tool_calls": [{"index": i, **fn}]}}]}


def test_stream_merges_openai_style_tool_call(monkeypatch):
    ev = run(monkeypatch, sse(tc(0, id="c1", function={"name": "exec", "arguments": ""}), tc(0, function={"arguments": '{"command":'}), tc(0, function={"arguments": '"ls"}'})))
    assert ev[-1]["tool_calls"] == [{"id": "c1", "name": "exec", "args": {"command": "ls"}}]


def test_stream_splits_gemini_style_calls_that_all_use_index_zero(monkeypatch):
    ev = run(monkeypatch, sse(tc(0, id="a", function={"name": "read", "arguments": '{"path":"x"}'}), tc(0, id="b", function={"name": "list_dir", "arguments": '{"path":"."}'})))
    assert [c["name"] for c in ev[-1]["tool_calls"]] == ["read", "list_dir"]


def test_stream_emits_thinking_and_usage(monkeypatch):
    ev = run(monkeypatch, sse({"choices": [{"delta": {"reasoning_content": "hmm"}}]}, {"choices": [{"delta": {"content": "ok"}}]}, {"choices": [], "usage": {"prompt_tokens": 3, "completion_tokens": 2}}))
    assert [e["type"] for e in ev] == ["thinking", "delta", "final"] and ev[-1]["usage"] == {"prompt": 3, "completion": 2}


def test_error_classification(monkeypatch):
    assert providers.ProviderError("x", 503).retryable and providers.ProviderError("x", 429).retryable
    assert not providers.ProviderError("x", 401).retryable and not providers.ProviderError("x", 404).retryable
    assert not providers.ProviderError("x", transient=False).retryable
    with pytest.raises(providers.ProviderError) as e:
        run(monkeypatch, [], status=503)
    assert e.value.status == 503 and e.value.retryable


def test_non_chat_models_filtered():
    for bad in ("gemini-3-flash-tts", "text-embedding-004", "imagen-4", "veo-3", "whisper-1"):
        assert providers.NON_CHAT.search(bad), bad
    for good in ("gemini-2.5-flash", "gpt-4o-mini", "qwen2.5:3b", "claude-sonnet-5-5"):
        assert not providers.NON_CHAT.search(good), good


def test_path_import():
    assert Path(__file__).exists()


def test_read_document_xlsx_csv_docx(tmp_path):
    import zipfile
    from openpyxl import Workbook
    c = ctx(tmp_path)
    wb = Workbook()
    wb.active.append(["ten", "so"])
    wb.active.append(["a", 1])
    wb.save(c.cwd / "d.xlsx")
    assert "ten\tso" in tools.call(c, "read_document", {"path": "d.xlsx"})[0]
    (c.cwd / "d.csv").write_text("x,y\n1,2")
    assert "x,y" in tools.call(c, "read_document", {"path": "d.csv"})[0]
    with zipfile.ZipFile(c.cwd / "d.docx", "w") as z:
        z.writestr("word/document.xml", "<w:p><w:t>Xin chao</w:t></w:p><w:p><w:t>the gioi</w:t></w:p>")
    out = tools.call(c, "read_document", {"path": "d.docx"})[0]
    assert "Xin chao" in out and "the gioi" in out


# ---------- che do quyen cua hoi thoai (readonly / guarded / full)
from nestor.services import agent as agent_mod  # noqa: E402


def test_readonly_hides_every_mutating_tool(tmp_path):
    c = ctx(tmp_path, lambda k, d: True)
    note = agent_mod.apply_permission(c, "readonly")
    names = {s["name"] for s in tools.schemas(c)}
    assert not names & {"write", "edit", "exec", "remember", "http_request"}
    assert {"read", "list_dir", "web_fetch", "web_search", "memory_search"} <= names and "CHỈ ĐỌC" in note
    assert not tools.call(c, "exec", {"command": "touch x"})[1] and not (c.cwd / "x").exists()


def test_readonly_keeps_only_read_only_mcp_tools(tmp_path):
    c = ctx(tmp_path)
    c.extra = {"s__ro": tools.ToolDef("s__ro", "d", {}, lambda ctx: "ok", "mcp", read_only=True),
               "s__rw": tools.ToolDef("s__rw", "d", {}, lambda ctx: "ok", "mcp", read_only=False)}
    agent_mod.apply_permission(c, "readonly")
    names = {s["name"] for s in tools.schemas(c)}
    assert "s__ro" in names and "s__rw" not in names


def test_guarded_asks_even_for_writes_inside_session_dir(tmp_path):
    asked = []
    c = ctx(tmp_path, lambda k, d: asked.append(k) or False)
    agent_mod.apply_permission(c, "guarded")
    out, ok = tools.call(c, "write", {"path": "a.txt", "content": "x"})
    assert not ok and asked == ["file_write"] and not (c.cwd / "a.txt").exists()
    c.approver = lambda k, d: True
    assert tools.call(c, "write", {"path": "a.txt", "content": "x"})[1] and (c.cwd / "a.txt").exists()


def test_default_does_not_ask_for_writes_inside_session_dir(tmp_path):
    asked = []
    c = ctx(tmp_path, lambda k, d: asked.append(k) or False)
    agent_mod.apply_permission(c, "default")
    assert tools.call(c, "write", {"path": "a.txt", "content": "x"})[1] and asked == []


def test_full_access_never_asks(tmp_path):
    asked = []
    c = ctx(tmp_path, lambda k, d: asked.append(k) or False)
    agent_mod.apply_permission(c, "full")
    outside = tmp_path / "outside.txt"
    outside.write_text("secret")
    assert tools.call(c, "read", {"path": str(outside)})[0] == "secret"
    assert tools.call(c, "exec", {"command": "echo hi"})[0].strip() == "hi" and asked == []


def test_reasoning_effort_only_sent_when_chosen(monkeypatch):
    sent = []

    def fake(*a, **k):
        sent.append(k["json"])
        return FakeStream(sse({"choices": [{"delta": {"content": "ok"}}]}))

    monkeypatch.setattr(providers.httpx, "stream", fake)
    cfg = ProviderCfg(base_url="http://x/v1", model="m")
    list(providers.OpenAICompat(cfg).stream([{"role": "user", "content": "hi"}], []))
    list(providers.OpenAICompat(cfg).stream([{"role": "user", "content": "hi"}], [], effort="high"))
    list(providers.OpenAICompat(cfg).stream([{"role": "user", "content": "hi"}], [], effort="bogus"))
    assert "reasoning_effort" not in sent[0] and sent[1]["reasoning_effort"] == "high" and "reasoning_effort" not in sent[2]


def test_openrouter_gets_default_max_tokens_and_retries_on_402(monkeypatch):
    sent = []

    def fake(*a, **k):
        sent.append(k["json"].get("max_tokens"))
        if len(sent) == 1:
            st = FakeStream([], status=402)
            st.text = '{"error":{"message":"You requested up to 16384 tokens, but can only afford 5000."}}'
            return st
        return FakeStream(sse({"choices": [{"delta": {"content": "ok"}}]}))

    monkeypatch.setattr(providers.httpx, "stream", fake)
    cfg = ProviderCfg(base_url="https://openrouter.ai/api/v1", model="anthropic/x")
    list(providers.OpenAICompat(cfg).stream([{"role": "user", "content": "hi"}], []))
    assert sent == [providers.OPENROUTER_DEFAULT_MAX, 5000 - 64]
    other = []
    monkeypatch.setattr(providers.httpx, "stream", lambda *a, **k: (other.append(k["json"].get("max_tokens")), FakeStream(sse({"choices": [{"delta": {"content": "ok"}}]})))[1])
    list(providers.OpenAICompat(ProviderCfg(base_url="http://x/v1", model="m")).stream([{"role": "user", "content": "hi"}], []))
    assert other == [None]


def test_openrouter_retries_prompt_limit_with_complete_recent_turns(monkeypatch):
    sent = []

    def fake(*args, **kwargs):
        sent.append(kwargs["json"])
        if len(sent) == 1:
            response = FakeStream([], status=402)
            response.text = '{"error":{"message":"Prompt tokens limit exceeded: 47633 > 39761. To increase, visit https://openrouter.ai/private"}}'
            return response
        return FakeStream(sse({"choices": [{"delta": {"content": "ok"}}]}))

    monkeypatch.setattr(providers.httpx, "stream", fake)
    cfg = ProviderCfg(base_url="https://openrouter.ai/api/v1", model="anthropic/x")
    current = {"role": "user", "content": "Viết chương trình Fibonacci"}
    messages = [
        {"role": "system", "content": "Chỉ dẫn hệ thống"},
        {"role": "user", "content": "Một lượt cũ"},
        {"role": "assistant", "content": "", "tool_calls": [{"id": "old", "name": "read", "args": {}}]},
        {"role": "tool", "tool_call_id": "old", "content": "dữ liệu " * 20_000},
        {"role": "user", "content": "Một lượt gần đây"},
        {"role": "assistant", "content": "Phản hồi"},
        current,
    ]
    tools = [{"name": "read", "description": "Read", "parameters": {}}]
    updates = []

    events = list(agent_mod._stream_with_retry("openrouter", cfg, messages, tools, updates.append, None, current=current))

    assert events[-1]["content"] == "ok"
    assert len(sent) == 2 and len(messages) == 7
    assert sent[1]["messages"] == [messages[0], *messages[4:]]
    assert sent[1]["tools"] == sent[0]["tools"]
    assert updates[0]["type"] == "status"


def test_openrouter_prompt_limit_error_does_not_expose_key_settings_url(monkeypatch):
    response = FakeStream([], status=402)
    response.text = '{"error":{"message":"Prompt tokens limit exceeded: 47633 > 39761. To increase, visit https://openrouter.ai/private"}}'
    monkeypatch.setattr(providers.httpx, "stream", lambda *args, **kwargs: response)
    cfg = ProviderCfg(base_url="https://openrouter.ai/api/v1", model="anthropic/x")
    current = {"role": "user", "content": "Một yêu cầu"}

    with pytest.raises(providers.PromptLimitError, match="47,633.*39,761") as exc:
        list(agent_mod._stream_with_retry("openrouter", cfg, [{"role": "system", "content": ""}, current], [], lambda _: None, None, current=current))

    assert "https://" not in str(exc.value)


def test_prompt_limit_compacts_large_skill_catalog_without_dropping_short_history():
    entry = '<skill category="office"><name>sample</name><description>Detailed guidance.</description></skill>'
    system = "Preserve permissions.\n<available_skills>\n" + ("  " + entry + "\n") * 100 + "</available_skills>\nPreserve system instructions."
    current = {"role": "user", "content": "Còn cách nào khác?"}
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": "Một câu hỏi ngắn"},
        {"role": "assistant", "content": "Một câu trả lời ngắn"},
        current,
    ]

    fitted = agent_mod._fit_prompt_limit(messages, [], current, providers.PromptLimitError(47_633, 39_761))

    assert fitted[1:] == messages[1:] and fitted[-1] is current
    assert "Preserve permissions." in fitted[0]["content"] and "Preserve system instructions." in fitted[0]["content"]
    assert fitted[0]["content"].count("- sample") == 100
    assert len(fitted[0]["content"]) < len(system)
    assert messages[0]["content"] == system


def test_context_anchor_shortens_large_tool_result_before_provider_call(monkeypatch):
    import time

    cfg = ProviderCfg(base_url="http://local/v1", model="model", context_window=8_000)
    current = {"role": "user", "content": "Read logs"}
    system = {"role": "system", "content": "System"}
    schemas = [{"name": "read", "parameters": {}}]
    anchor = {**agent_mod.context_report([system, current], schemas, cfg, current),
              "prompt_tokens": 6_000, "ts": time.time()}
    call = {"role": "assistant", "content": "", "tool_calls": [{"id": "one", "name": "read", "args": {}}]}
    result = {"role": "tool", "tool_call_id": "one", "content": "start " + "x" * 24_000 + " end"}
    sent = []

    def fake(*args, **kwargs):
        sent.append(kwargs["json"])
        return FakeStream(sse({"choices": [{"delta": {"content": "ok"}}]}))

    monkeypatch.setattr(providers.httpx, "stream", fake)
    report = {}
    list(agent_mod._stream_with_retry("local", cfg, [system, current, call, result], schemas, lambda _: None, None,
                                      current=current, report=report, previous=anchor))

    assert len(sent) == 1 and report["anchored_tokens"] is not None
    actual = sent[0]["messages"]
    assert actual[1] == current
    assert actual[2]["tool_calls"][0]["id"] == actual[3]["tool_call_id"]
    assert actual[3]["content"].startswith("start ") and actual[3]["content"].endswith(" end")
    assert len(actual[3]["content"]) < len(result["content"])
