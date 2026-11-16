import hashlib
import json
import threading

import pytest
from fastapi.testclient import TestClient

from nestor.core import config as cfgmod
from nestor.main import app
from nestor.services import assistants, brief, distill, jobs, rules, scheduler, sessions, teams, tools, tools_agents, zalo_channel
from nestor.services.tools import ToolContext


@pytest.fixture
def client(tmp_env):
    return TestClient(app, headers={"host": "localhost"})


def ctx(tmp_path, **kw):
    return ToolContext(workspace=tmp_path, cwd=tmp_path, full_access=True, **kw)


# ---- 1. tro ly
def test_assistants_api_builtin_and_custom(client):
    items = client.get("/api/assistants").json()
    ids = {a["id"] for a in items}
    assert {"van-thu-nd30", "van-ban-dang-hd05", "tong-hop-bao-cao", "thu-ky", "ke-toan", "nhan-su", "kinh-doanh-marketing", "quan-ly-du-an", "phap-che", "it"} <= ids
    a = next(a for a in items if a["id"] == "van-thu-nd30")
    assert len(a["starters"]) == 3 and "vanban_write_docx" in a["prompt"] and a["group"] == "co-quan"
    body = {"name": "Trợ lý phòng", "prompt": "Luôn ký thừa lệnh", "starters": ["a"]}
    assert client.post("/api/assistants/phong-a", json=body).status_code == 200
    assert client.post("/api/assistants/phong-a", json=body).status_code == 400  # trung id
    assert client.put("/api/assistants/phong-a", json={**body, "name": "Mới"}).json()["name"] == "Mới"
    assert client.put("/api/assistants/van-thu-nd30", json=body).status_code == 400
    assert any(a["id"] == "phong-a" and not a["builtin"] for a in client.get("/api/assistants").json())
    assert "Luôn ký" in assistants.prompt_for("phong-a")
    assert client.delete("/api/assistants/phong-a").status_code == 200
    assert client.delete("/api/assistants/it").status_code == 400
    assert assistants.prompt_for("khong-co") == ""


def test_chat_passes_assistant_prompt(client, monkeypatch):
    seen = {}

    def fake(*a, **kw):
        seen.update(kw)
        yield {"type": "done"}
    from nestor.services import chat_runner
    monkeypatch.setattr(chat_runner, "stream_chat", fake)
    client.post("/api/chat", json={"text": "hi", "assistant": "ke-toan"})
    assert "kế toán" in seen["system_extra"].lower()


# ---- 2. ra soat the thuc
def test_review_vn_document(tmp_path):
    c = ctx(tmp_path)
    import json
    from test_office import to_trinh_paragraphs
    tools.call(c, "vanban_write_docx", {"path": "ok", "document_type_key": "TO_TRINH", "paragraphs": json.dumps(to_trinh_paragraphs()), "ngan_theo_yeu_cau": True})
    out, ok = tools.call(c, "review_vn_document", {"path": "ok.docx"})
    assert ok and "0 lỗi" not in out and "đạt" in out and "[LỖI]" not in out, out
    tools.call(c, "create_docx", {"path": "bad", "content": "Gửi UBND huyện A\nNội dung thiếu hết."})
    out, _ = tools.call(c, "review_vn_document", {"path": "bad.docx"})
    assert "[LỖI] Quốc hiệu" in out and "[LỖI] Nơi nhận" in out and "huyện" in out and "[LỖI] Số, ký hiệu" in out


# ---- 3. zalo
SECRET = "s3cret"


def _zalo_cfg(**kw):
    cfg = cfgmod.load()
    z = cfg.channels.zalo
    z.enabled, z.app_id, z.access_token, z.refresh_token, z.app_secret, z.webhook_secret = True, "app1", "tok", "ref", "sec", SECRET
    z.allowed_users = kw.get("users", [])
    cfgmod.save(cfg)
    return cfg.channels.zalo


def test_zalo_config_api_masks_and_requires_secret(client):
    r = client.put("/api/channels/zalo", json={"enabled": True, "access_token": "t"})
    assert r.status_code == 400
    r = client.put("/api/channels/zalo", json={"enabled": True, "oa_id": "1", "app_id": "a", "access_token": "t", "webhook_secret": SECRET}).json()
    assert r["has_access_token"] and r["running"] and "access_token" not in r
    assert client.put("/api/channels/zalo", json={"enabled": True, "access_token": "***", "webhook_secret": "***"}).status_code == 200
    assert cfgmod.load().channels.zalo.access_token == "t"
    assert client.get("/api/channels").json()["zalo"]["enabled"]
    assert len(client.post("/api/channels/zalo/pair-code").json()["code"]) == 6


def test_zalo_webhook_auth_and_pairing_and_reply(client, monkeypatch):
    _zalo_cfg()
    sent, done = [], threading.Event()

    def fake_say(self, uid, text):
        sent.append((uid, text))
        done.set()
    monkeypatch.setattr(zalo_channel.ZaloChannel, "say", fake_say)
    ev = {"event_name": "user_send_text", "sender": {"id": "u1"}, "message": {"text": "/id"}, "timestamp": "123"}
    raw = json.dumps(ev).encode()
    assert client.post("/api/channels/zalo/webhook", content=raw).status_code == 403
    assert client.post("/api/channels/zalo/webhook?secret=bad", content=raw).status_code == 403
    sig = hashlib.sha256(f"app1{raw.decode()}123{SECRET}".encode()).hexdigest()
    assert client.post("/api/channels/zalo/webhook", content=raw, headers={"X-ZEvent-Signature": "mac=" + sig}).status_code == 200
    assert done.wait(5) and "u1" in sent[0][1]
    # ghep doi
    code = zalo_channel.new_pair_code()
    done.clear()
    client.post(f"/api/channels/zalo/webhook?secret={SECRET}", json={**ev, "message": {"text": f"/pair {code}"}})
    assert done.wait(5)
    assert "u1" in cfgmod.load().channels.zalo.allowed_users


def test_zalo_run_replies_with_agent_text(tmp_env, monkeypatch):
    _zalo_cfg(users=["u1"])
    from nestor.services import chat_runner
    monkeypatch.setattr(chat_runner, "stream_chat", lambda sid, text, prov, **kw: iter([{"type": "assistant", "content": "Xin chào [[src:a|Doc|tr.2]]"}, {"type": "done"}]))
    ch = zalo_channel.ZaloChannel()
    out = []
    monkeypatch.setattr(ch, "say", lambda uid, t: out.append(t))
    ch._handle("u1", "chào")  # noqa: SLF001
    assert out[0].startswith("Xin chào")
    ch._handle("u9", "chào")  # noqa: SLF001
    assert "chưa được phép" in out[-1]


def test_zalo_api_refreshes_expired_token(tmp_env, monkeypatch):
    _zalo_cfg()
    calls = []

    class R:
        def __init__(self, d): self.d = d
        def json(self): return self.d

    def fake_post(url, **kw):
        calls.append(url)
        if "access_token" in url and "oauth" in url:
            return R({"access_token": "new", "refresh_token": "ref2"})
        return R({"error": -216, "message": "expired"} if kw["headers"]["access_token"] == "tok" else {"error": 0})
    monkeypatch.setattr(zalo_channel.httpx, "post", fake_post)
    ch = zalo_channel.ZaloChannel()
    ch.apply(cfgmod.load().channels.zalo)
    ch.say("u1", "hi")
    assert cfgmod.load().channels.zalo.access_token == "new" and cfgmod.load().channels.zalo.refresh_token == "ref2"
    assert sum("cs" in c for c in calls) == 2


# ---- 4. morning brief
def test_morning_brief_endpoint_idempotent(client):
    r = client.post("/api/automations/templates/morning-brief", json={"time": "07:30"}).json()
    assert r["schedule"] == "30 7 * * *" and not r["updated"]
    r2 = client.post("/api/automations/templates/morning-brief", json={"time": "06:15"}).json()
    assert r2["id"] == r["id"] and r2["updated"]
    jobs_ = [j for j in scheduler.list_jobs() if j["name"] == brief.NAME]
    assert len(jobs_) == 1 and jobs_[0]["schedule"] == "15 6 * * *" and jobs_[0]["notify"]
    assert client.post("/api/automations/templates/morning-brief", json={"time": "25:00"}).status_code == 400


# ---- 5. distill + rules
def test_distill_skill_and_rule(client, monkeypatch):
    sid = sessions.create("t")
    sessions.add_message(sid, {"role": "user", "content": "Soạn tờ trình, nhớ ký thừa lệnh"})
    sessions.add_message(sid, {"role": "assistant", "content": "Đã soạn xong."})
    monkeypatch.setattr(distill, "_ask", lambda prompt, provider=None: "DESCRIPTION: Soạn tờ trình ký thừa lệnh\n# Soạn tờ trình\n## Các bước\n1. Hỏi cơ quan" if "kỹ năng" in prompt else "Văn bản của phòng luôn ký thừa lệnh.")
    r = client.post(f"/api/sessions/{sid}/distill", json={"kind": "skill"}).json()
    assert r["kind"] == "skill" and r["name"] == "soan-to-trinh" and "name: soan-to-trinh" in r["content"]
    assert (cfgmod.load().workspace_path() / "skills" / "soan-to-trinh" / "SKILL.md").exists()
    r = client.post(f"/api/sessions/{sid}/distill", json={"kind": "rule"}).json()
    assert r["text"].startswith("Văn bản của phòng")
    assert client.get("/api/rules").json() == [{"id": 0, "text": r["text"]}]
    from nestor.services import agent
    sp = agent.build_system_prompt(cfgmod.load(), {}, "/tmp")
    assert "ký thừa lệnh" in sp
    assert client.delete("/api/rules/0").status_code == 200 and client.get("/api/rules").json() == []
    assert client.delete("/api/rules/5").status_code == 404
    assert client.post("/api/sessions/nope/distill", json={"kind": "rule"}).status_code == 400
    assert rules.add("a")["id"] == 0


# ---- 6. to cong tac
def test_team_run_parallel_with_notes_and_review(tmp_env, monkeypatch):
    calls, lock = [], threading.Lock()

    def fake_sub(c, role, task):
        with lock:
            calls.append((role, task))
        if role == "reviewer":
            return {"id": "rv", "status": "done", "result": "Rà xong, khớp.", "error": None}
        tid = task.split("tổ công tác ")[1].split(" ")[0]
        teams.note_write(tid, f"n-{role}", f"số liệu {role}", role)
        return {"id": f"j-{role}", "status": "done" if role != "coder" else "failed", "result": f"kq {role}", "error": "hỏng" if role == "coder" else None}
    monkeypatch.setattr(jobs, "run_subagent", fake_sub)
    c = ctx(tmp_env, session_id="s")
    c.depth = 0
    events = []
    c.emit = events.append
    out = tools_agents.team_run(c, "Tổng hợp", json.dumps([{"role": "researcher", "task": "A"}, {"role": "coder", "task": "B"}]))
    assert "kq researcher" in out and "hỏng" in out and "Rà xong" in out and "partial" in out
    assert events[0]["type"] == "team"
    tid = events[0]["id"]
    t = teams.get(tid)
    assert t["status"] == "partial" and {m["status"] for m in t["members"]} == {"done", "failed"} and set(t["notes"]) == {"n-researcher", "n-coder"}
    assert [r for r, _ in calls].count("reviewer") == 1
    assert "số liệu researcher" in tools_agents.team_note_read(c, tid)


def test_team_status_api_and_limits(client, tmp_env):
    t = teams.create("g", [{"role": "general", "task": "x"}], None)
    assert client.get(f"/api/teams/{t['id']}/status").json()["members"][0]["status"] == "queued"
    assert client.get("/api/teams/zzz/status").status_code == 404
    assert any(x["id"] == t["id"] for x in client.get("/api/teams").json())
    c = ctx(tmp_env)
    c.depth = 5
    with pytest.raises(ValueError):
        tools_agents.team_run(c, "g", '[{"role":"general","task":"x"}]')
    c.depth = 0
    with pytest.raises(ValueError):
        tools_agents.team_run(c, "g", "[]")


# ---- 7. run_script
def test_run_script_and_save_as_skill(tmp_env):
    called = []
    c = ToolContext(workspace=tmp_env, cwd=tmp_env, approver=lambda k, d: called.append(k) or True)
    out, ok = tools.call(c, "run_script", {"name": "x.py", "code": "print('xin chào')\nimport sys; sys.stderr.write('e')"})
    assert ok and "xin chào" in out and "mã thoát 0" in out and called == ["exec"] and (tmp_env / "scripts" / "x.py").exists()
    c.approver = lambda k, d: False
    out, _ = tools.call(c, "run_script", {"name": "y.py", "code": "print(1)"})
    assert "KHÔNG THỰC HIỆN" in out
    out, _ = tools.call(ctx(tmp_env), "run_script", {"name": "t.py", "code": "import time; time.sleep(30)", "timeout": 5})
    assert "quá 5s" in out
    _, ok = tools.call(ctx(tmp_env), "run_script", {"name": "../evil.txt", "code": "x"})
    assert not ok
    out, ok = tools.call(ctx(tmp_env), "save_script_as_skill", {"name": "gop-bao-cao", "description": "Gộp báo cáo", "script_path": "scripts/x.py"})
    assert ok, out
    d = cfgmod.load().workspace_path() / "skills" / "gop-bao-cao"
    assert (d / "SKILL.md").exists() and (d / "scripts" / "x.py").exists()
    assert not tools.call(ctx(tmp_env), "save_script_as_skill", {"name": "Bad Name", "description": "d", "script_path": "scripts/x.py"})[1]
