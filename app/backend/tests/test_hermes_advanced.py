"""Kiểm tra toàn diện 6 kỹ thuật nâng cao học hỏi từ Hermes Agent:
1. Self-Healing Tool Calls (Chẩn đoán & tự sửa lỗi tham số công cụ)
2. Post-Action Verification (Tự kiểm chứng tệp rỗng, lỗi cú pháp, placeholder)
3. Context Checkpoint & Backtracking (Quay lui khi vào ngõ cụt)
4. Adaptive Reasoning Scratchpad (Quy trình suy luận đa pha)
5. Subagent Swarm (Bầy agent điều phối chuyên biệt)
6. Dynamic Few-Shot Exemplars (Tiêm động ví dụ mẫu theo ngữ cảnh)
"""
import json
from pathlib import Path
import pytest

from nestor.core import config as cfgmod
from nestor.services import agent, checkpoints, tools
from nestor.services.agent.self_healing import diagnose_tool_call
from nestor.services.agent.verification import verify_file, verify_turn_outputs
from nestor.services.agent.exemplars import get_dynamic_exemplars


def test_self_healing_missing_argument():
    tdef = tools.TOOLS.get("read")
    assert tdef is not None
    # Gọi thiếu tham số bắt buộc 'path'
    diag = diagnose_tool_call("read", tdef, {}, TypeError("missing required argument 'path'"))
    assert "THIẾU THAM SỐ BẮT BUỘC" in diag
    assert "`path`" in diag
    assert "HƯỚNG DẪN TỰ SỬA" in diag


def test_self_healing_typo_argument():
    tdef = tools.TOOLS.get("read")
    # Truyền nhầm 'file' thay vì 'path'
    diag = diagnose_tool_call("read", tdef, {"file": "test.txt"}, TypeError("unexpected keyword argument 'file'"))
    assert "SAI TÊN THAM SỐ" in diag
    assert "path" in diag


def test_self_healing_invalid_json():
    tdef = tools.TOOLS.get("create_cv")
    diag = diagnose_tool_call("create_cv", tdef, {"path": "a.pdf", "template": "m", "data": "{invalid_json"}, ValueError("JSONDecodeError"))
    assert "JSON bị lỗi cú pháp" in diag or "CẤU TRÚC THAM SỐ HỢP LỆ" in diag


def test_post_action_verification_empty_file(tmp_path):
    empty_f = tmp_path / "empty.txt"
    empty_f.write_text("")
    issues = verify_file(empty_f)
    assert any("0 bytes" in s for s in issues)


def test_post_action_verification_syntax_error(tmp_path):
    bad_py = tmp_path / "broken.py"
    bad_py.write_text("def broken_func(:\n    pass\n")
    issues = verify_file(bad_py)
    assert any("cú pháp" in s for s in issues)

    bad_json = tmp_path / "broken.json"
    bad_json.write_text('{"name": "test",}')
    issues_json = verify_file(bad_json)
    assert any("cú pháp" in s for s in issues_json)


def test_post_action_verification_placeholders(tmp_path):
    todo_f = tmp_path / "doc.txt"
    todo_f.write_text("Dự án này sẽ do {{TODO}} phụ trách vào ngày [Điền vào đây].")
    issues = verify_file(todo_f)
    assert any("chưa điền" in s for s in issues)


def test_post_action_verification_valid_file(tmp_path):
    good_py = tmp_path / "good.py"
    good_py.write_text("def add(a: int, b: int) -> int:\n    return a + b\n")
    assert not verify_file(good_py)


def test_backtrack_tool(tmp_env):
    cfg = cfgmod.load()
    sid = "test-backtrack-session"
    ws = tmp_env / "workspace"
    ws.mkdir(parents=True, exist_ok=True)
    checkpoints.begin(sid)

    file_to_modify = ws / "target.txt"
    file_to_modify.write_text("ban dau")
    checkpoints.record(sid, file_to_modify)

    # Thay đổi file
    file_to_modify.write_text("da bi sua sai")
    checkpoints.finish(sid)

    ctx = tools.ToolContext(workspace=ws, cwd=ws)
    ctx.session_id = sid

    out, ok = tools.call(ctx, "backtrack", {"reason": "thu nghiem sai huong"})
    assert ok
    assert "ĐÃ QUAY LUI THÀNH CÔNG" in out
    assert file_to_modify.read_text() == "ban dau"


def test_adaptive_scratchpad_in_system_prompt():
    cfg = cfgmod.load()
    prompt = agent.build_system_prompt(cfg, {}, cfg.workspace_path())
    assert "Hermes Reasoning Scratchpad" in prompt
    assert "Quan sát" in prompt and "Kế hoạch" in prompt


def test_dynamic_few_shot_exemplars():
    # Câu hỏi về lập trình
    coding_ex = get_dynamic_exemplars("Hãy giúp tôi debug hàm python và sửa lỗi cú pháp")
    assert "Mẫu giải quyết bài toán Lập trình" in coding_ex
    assert "edit thay vì ghi đè" in coding_ex

    # Câu hỏi về nghị định 30
    nd30_ex = get_dynamic_exemplars("Soạn tờ trình xin kinh phí theo nghị định 30")
    assert "Nghị định 30/2020/NĐ-CP" in nd30_ex
    assert "vanban_types" in nd30_ex

    # Câu hỏi chung chung không thuộc domain đặc thù -> không tốn token
    general_ex = get_dynamic_exemplars("Hôm nay là ngày mấy?")
    assert general_ex == ""


def test_swarm_run_tool_registered():
    assert "swarm_run" in tools.TOOLS
    t = tools.TOOLS["swarm_run"]
    assert "Hermes Swarm Protocol" in t.description
