import json
from pathlib import Path

from nestor.services import agent, hooks, tools


def _ctx(tmp_path, **kw):
    return tools.ToolContext(workspace=tmp_path, cwd=tmp_path, **kw)


def test_hook_blocks_tool(tmp_path):
    (tmp_path / "hooks.json").write_text(json.dumps({"PreToolUse": [{"matcher": "write", "command": "echo cam >&2; exit 2"}]}))
    out, ok = tools.call(_ctx(tmp_path), "write", {"path": "a.txt", "content": "x"})
    assert not ok and "cam" in out and not (tmp_path / "a.txt").exists()


def test_post_hook_runs(tmp_path):
    (tmp_path / "hooks.json").write_text(json.dumps({"PostToolUse": [{"matcher": "write", "command": "touch done.flag"}]}))
    out, ok = tools.call(_ctx(tmp_path), "write", {"path": "a.txt", "content": "x"})
    assert ok and (tmp_path / "done.flag").exists()


def test_hook_matcher_skips_other_tools(tmp_path):
    (tmp_path / "hooks.json").write_text(json.dumps({"PreToolUse": [{"matcher": "exec", "command": "exit 2"}]}))
    assert hooks.run(_ctx(tmp_path), "PreToolUse", "read", {}) is None


def test_plan_mode_blocks_then_approves(tmp_path):
    ctx = _ctx(tmp_path, asker=lambda q, o: "Duyệt, bắt đầu làm")
    ctx.permission = "plan"
    assert "KẾ HOẠCH" in agent.apply_permission(ctx, "plan")
    assert not ctx.enabled["write"] and not ctx.enabled["exec"]
    assert "ĐÃ DUYỆT" in tools.plan_submit(ctx, "buoc 1")
    assert ctx.enabled.get("write", True) and ctx.permission == "default"


def test_plan_mode_rejected_stays_locked(tmp_path):
    ctx = _ctx(tmp_path, asker=lambda q, o: "Sửa lại kế hoạch")
    ctx.permission = "plan"
    agent.apply_permission(ctx, "plan")
    assert "chưa duyệt" in tools.plan_submit(ctx, "x") and not ctx.enabled["write"]


def test_project_docs_walks_parents(tmp_path, monkeypatch):
    monkeypatch.setattr(Path, "home", lambda: tmp_path / "home")
    (tmp_path / "AGENTS.md").write_text("ROOT RULE")
    sub = tmp_path / "pkg"
    sub.mkdir()
    (sub / "CLAUDE.md").write_text("SUB RULE")
    text = agent._project_docs(sub)
    assert "ROOT RULE" in text and "SUB RULE" in text and text.index("ROOT") < text.index("SUB")


def test_plan_finalize_closes_last_report_step(tmp_env):
    from nestor.services import plans
    plans.set_items("s1", ["a", "b", "c"])
    plans.update("s1", 1, "done"); plans.update("s1", 2, "done"); plans.update("s1", 3, "in_progress")
    out = plans.finalize("s1")
    assert [i["status"] for i in out] == ["done", "done", "done"]
    plans.set_items("s2", ["a", "b", "c"])
    plans.update("s2", 1, "done")
    assert plans.finalize("s2") is None  # con 2 buoc chua xong: khong tu dong dong
    plans.set_items("s3", ["a", "b"])
    plans.update("s3", 1, "done")
    assert [i["status"] for i in plans.finalize("s3")] == ["done", "done"]


def test_plan_finalize_does_not_close_never_started_step(tmp_env):
    from nestor.services import plans
    plans.set_items("s4", ["a", "b"])
    plans.update("s4", 1, "in_progress")
    assert [i["status"] for i in plans.finalize("s4")] == ["done", "pending"]
