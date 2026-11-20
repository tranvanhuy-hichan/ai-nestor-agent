"""Regression checks for the new execution boundaries on the web."""
import os

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from nestor.core import config
from nestor.main import app
from nestor.services import auth, jobs, sessions, tools


def test_terminal_requires_authenticated_same_origin(tmp_env, monkeypatch):
    if os.name != "posix":
        pytest.skip("PTY is available on POSIX")
    monkeypatch.setenv("NESTOR_WEB_TERMINAL", "1")
    monkeypatch.setattr(auth, "DATA", tmp_env)
    cfg = config.load()
    auth.set_password(cfg, "only-for-the-test")
    config.save(cfg)
    client = TestClient(app)

    with pytest.raises(WebSocketDisconnect) as anonymous:
        with client.websocket_connect("/api/terminal", headers={"Origin": "http://testserver"}):
            pytest.fail("an anonymous client opened a shell")
    assert anonymous.value.code == 1008
    assert client.post("/api/auth/login", json={"password": "only-for-the-test"}).status_code == 200

    with pytest.raises(WebSocketDisconnect) as cross_origin:
        with client.websocket_connect("/api/terminal", headers={"Origin": "http://another-origin.test"}):
            pytest.fail("a cross-origin client opened a shell")
    assert cross_origin.value.code == 1008


def test_per_tool_rules_apply_even_with_full_permissions(tmp_env):
    approved = []
    ctx = tools.ToolContext(
        workspace=tmp_env, full_access=True, confirm_exec=False,
        approver=lambda kind, detail: approved.append((kind, detail)) or True,
        policies={
            "list_dir": config.ToolPolicy(enabled=False),
            "read": config.ToolPolicy(approval="once", output_limit=100),
        },
    )
    (tmp_env / "many-characters.txt").write_text("result " * 40)
    assert "list_dir" not in {item["name"] for item in tools.schemas(ctx)}
    assert not tools.call(ctx, "list_dir", {"path": "."})[1]
    for _ in range(2):
        result, ok = tools.call(ctx, "read", {"path": "many-characters.txt"})
        assert ok and len(result) == 100
    assert len(approved) == 1
    external = tools.ToolContext(workspace=tmp_env, policies={"exec": config.ToolPolicy(approval="auto")})
    assert tools.call(external, "exec", {"command": "echo policy-test"})[0] == tools.DENIED


def test_profile_scope_is_preserved_for_history_and_jobs(tmp_env):
    client = TestClient(app)
    data = {"name": "Private memories", "prompt": "Use only the selected skills.", "scoped": True, "tools": []}
    assert client.post("/api/assistants/private", json=data).status_code == 200
    sid = client.post("/api/sessions", json={"assistant": "private"}).json()["id"]
    scope = sessions.get(sid)["assistant_scope"]
    assert scope
    sessions.add_message(sid, {"role": "user", "content": "Unique scope marker"})
    assert client.put(f"/api/sessions/{sid}/assistant", json={"assistant": ""}).status_code == 409

    child = jobs.get(jobs.create("Background task", parent_session=sid))
    assert child["assistant_scope"] == scope
    private_ctx = tools.ToolContext(workspace=tmp_env, profile_id=scope)
    public_ctx = tools.ToolContext(workspace=tmp_env)
    tools.remember(private_ctx, "Unique scope marker")
    assert "Unique scope marker" in tools.call(private_ctx, "memory_search", {"query": "scope marker"})[0]
    assert "Unique scope marker" not in tools.call(public_ctx, "memory_search", {"query": "scope marker"})[0]
    assert scope == sessions.get(sid)["assistant_scope"]
