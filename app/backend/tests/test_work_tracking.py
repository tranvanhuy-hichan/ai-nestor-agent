import threading
import time

from fastapi.testclient import TestClient

from nestor.core import config as cfgmod
from nestor.core.db import db
from nestor.main import app
from nestor.services import agent, chat_runner, distill, sessions, skills, workfiles
from nestor.services.system import work_runs


def test_automation_history_preserves_runs_and_rejects_concurrent_launch(tmp_env, monkeypatch):
    entered = threading.Event()
    release = threading.Event()
    outcomes = iter(("success", "error"))

    def fake_turn(sid, text, provider, approver, emit, **kwargs):
        entered.set()
        assert release.wait(4)
        if next(outcomes) == "error":
            emit({"type": "error", "message": "Example failure"})
            return
        base = workfiles.workdir_for(cfgmod.load(), sid)
        base.mkdir(parents=True, exist_ok=True)
        (base / "report.txt").write_text("example")
        emit({"type": "assistant", "content": "Report ready"})

    monkeypatch.setattr(agent, "run_turn", fake_turn)
    client = TestClient(app)
    job_id = client.post("/api/automations", json={
        "name": "Weekly report", "schedule": "0 8 * * 1", "prompt": "Make a report", "notify": False,
    }).json()["id"]
    next_run = client.get("/api/automations").json()[0]["next_run"]
    first = client.post(f"/api/automations/{job_id}/run").json()["id"]
    assert entered.wait(4)
    assert client.post(f"/api/automations/{job_id}/run").status_code == 409
    assert client.get(f"/api/automations/{job_id}/runs").json()[0]["status"] == "running"
    release.set()

    def completed(run_id):
        end = time.monotonic() + 4
        while time.monotonic() < end:
            runs = client.get(f"/api/automations/{job_id}/runs").json()
            if runs[0]["id"] == run_id and runs[0]["finished"]:
                return runs
            time.sleep(0.03)
        raise AssertionError("Automation failed to finish")

    first_run = completed(first)[0]
    assert first_run["trigger"] == "manual"
    assert first_run["output"] == "Report ready" and first_run["status"] == "ok"
    assert first_run["finished"] >= first_run["started"]
    assert first_run["files"] == ["report.txt"] and first_run["session_id"]
    second = client.post(f"/api/automations/{job_id}/run").json()["id"]
    runs = completed(second)
    assert [r["id"] for r in runs] == [second, first]
    assert runs[0]["status"] == "error" and runs[0]["output"] == "Example failure"
    assert client.get("/api/automations").json()[0]["next_run"] == next_run


def test_waiting_chat_replays_approval_and_updates_board(tmp_env, monkeypatch):
    sid = sessions.create(" existing chat")
    sessions.add_message(sid, {"role": "user", "content": "older message"})
    monkeypatch.setattr(chat_runner, "_auto_name_session", lambda *args: None)

    def fake_turn(sid, text, provider, approver, emit, cancel, *args, **kwargs):
        sessions.add_message(sid, {"role": "user", "content": text})
        emit({"type": "delta", "text": "Partial answer"})
        assert approver("file_write", "Write report")
        emit({"type": "assistant", "content": "Final report"})

    monkeypatch.setattr(agent, "run_turn", fake_turn)
    stream = chat_runner.stream_chat(sid, "Write a report", None, detach=True, attachments=["source.txt"])
    run_id = next(stream)["run_id"]
    assert next(stream)["text"] == "Partial answer"
    approval = next(stream)
    assert approval["type"] == "approval"
    stream.close()
    client = TestClient(app)
    state = client.get(f"/api/sessions/{sid}/run").json()
    assert state["run_id"] == run_id and state["base_count"] == 1
    assert state["user"] == {"text": "Write a report", "attachments": ["source.txt"]}
    assert client.get("/api/kanban/runs").json()[0]["status"] == "waiting"
    assert client.get(f"/api/sessions/{sid}/attach?run_id=stale").status_code == 409
    assert client.post(f"/api/sessions/{sid}/stop?run_id=stale").json() == {"ok": False}
    assert client.post(f"/api/approvals/{approval['id']}", json={"ok": True}).json() == {"ok": True}
    replay = client.get(f"/api/sessions/{sid}/attach", params={"run_id": run_id, "start": 0}).text
    assert "Partial answer" in replay and approval["id"] in replay and "Final report" in replay
    finished = client.get("/api/kanban/runs").json()[0]
    assert finished["status"] == "ok" and finished["output"] == "Final report"
    with db() as conn:
        work_runs.begin(conn, "interrupted", "cron", "In progress", job_id="job")
    work_runs.recover_interrupted()
    assert work_runs.recent(10, job_id="job")[0]["status"] == "interrupted"


def test_skill_draft_can_be_reviewed_and_cannot_overwrite_stale_content(tmp_env, monkeypatch):
    sid = sessions.create("Draft")
    sessions.add_message(sid, {"role": "user", "content": "Generate reports"})
    monkeypatch.setattr(distill, "_ask", lambda *_: "DESCRIPTION: New report procedure\n# Weekly report\nDo the work")
    cfg = cfgmod.load()
    existing = skills.create(cfg, "weekly-report", "Existing description", "Existing steps")
    skill_file = existing.path / "SKILL.md"
    original = skill_file.read_text()
    client = TestClient(app)
    response = client.post(f"/api/sessions/{sid}/skill-draft", json={})
    assert response.status_code == 200
    draft = response.json()
    assert draft["matches"][0]["body"] == "Existing steps"
    assert skill_file.read_text() == original
    payload = {key: draft[key] for key in ("name", "description", "body")}
    assert client.post("/api/skills/draft/save", json=payload).status_code == 409
    payload["revision"] = draft["matches"][0]["revision"]
    assert client.post("/api/skills/draft/save", json=payload).status_code == 200
    assert "Do the work" in skill_file.read_text()
    assert client.post("/api/skills/draft/save", json=payload).status_code == 409
    payload.pop("revision")
    payload["name"] = "monthly-report"
    assert client.post("/api/skills/draft/save", json=payload).status_code == 200
