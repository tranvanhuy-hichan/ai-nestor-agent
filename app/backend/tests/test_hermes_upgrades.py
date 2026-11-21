"""Kiểm thử các tính năng nâng cấp lấy cảm hứng từ Hermes Agent:
1. Truncation thông minh (Head-Tail with Middle Elision).
2. LoopGuard & Stuck Detector (phát hiện lặp tool đơn và chu kỳ ping-pong).
3. SkillCurator & Vòng đời kỹ năng (thống kê lượt dùng, ghim, lưu trữ, khôi phục).
4. Chuẩn hóa Skill Index Level 0 (category và mô tả cô đọng).
"""
import json
import time
from pathlib import Path
import pytest

from nestor.services.truncation import truncate_middle
from nestor.services.loop_guard import LoopGuard
from nestor.services import skill_curator, skills as skillmod
from nestor.services.tools import ToolContext, call


def test_truncate_middle_short_text():
    short = "Hello world"
    assert truncate_middle(short, max_chars=100) == short


def test_truncate_middle_long_text():
    lines = [f"Line {i:04d}: This is some sample log content for testing truncation." for i in range(200)]
    long_text = "\n".join(lines)
    max_c = 1000
    res = truncate_middle(long_text, max_chars=max_c, head_ratio=0.4)
    assert len(res) < len(long_text)
    assert "Đã ẩn" in res
    assert "Line 0000" in res  # Head preserved
    assert "Line 0199" in res  # Tail preserved


def test_loop_guard_detects_consecutive_duplicates():
    guard = LoopGuard(max_consecutive_duplicates=3)
    call_1 = {"name": "exec", "args": {"command": "npm test"}}
    
    stuck, _, _ = guard.record_and_check([call_1])
    assert not stuck
    stuck, _, _ = guard.record_and_check([call_1])
    assert not stuck
    stuck, warn, notice = guard.record_and_check([call_1])
    assert stuck
    assert "PHÁT HIỆN KẸT VÒNG LẶP" in warn
    assert "npm test" in warn
    assert "LoopGuard: Phát hiện lặp công cụ 'exec'" in notice


def test_loop_guard_detects_ping_pong_cycles():
    guard = LoopGuard()
    call_a = {"name": "read", "args": {"path": "a.txt"}}
    call_b = {"name": "grep", "args": {"pattern": "foo"}}

    stuck, _, _ = guard.record_and_check([call_a])
    assert not stuck
    stuck, _, _ = guard.record_and_check([call_b])
    assert not stuck
    stuck, _, _ = guard.record_and_check([call_a])
    assert not stuck
    stuck, warn, notice = guard.record_and_check([call_b])
    assert stuck
    assert "PING-PONG LOOP" in warn
    assert "LoopGuard: Phát hiện vòng lặp luân phiên" in notice


def test_loop_guard_normal_calls_pass():
    guard = LoopGuard()
    calls = [
        {"name": "read", "args": {"path": f"file_{i}.txt"}}
        for i in range(10)
    ]
    for c in calls:
        stuck, _, _ = guard.record_and_check([c])
        assert not stuck


def test_skill_curator_lifecycle(tmp_path: Path):
    ws = tmp_path / "workspace"
    ws_skills = ws / "skills"
    ws_skills.mkdir(parents=True)

    # Tạo 2 skill giả lập
    s1 = ws_skills / "active-skill"
    s1.mkdir()
    (s1 / "SKILL.md").write_text("---\nname: active-skill\ndescription: Active test skill\n---\nBody")

    s2 = ws_skills / "stale-skill"
    s2.mkdir()
    (s2 / "SKILL.md").write_text("---\nname: stale-skill\ndescription: Stale test skill\n---\nBody")

    s3 = ws_skills / "pinned-stale"
    s3.mkdir()
    (s3 / "SKILL.md").write_text("---\nname: pinned-stale\ndescription: Pinned stale skill\n---\nBody")

    # 1. Ghi nhận lượt dùng
    info = skill_curator.record_usage("active-skill", base_dir=ws)
    assert info["use_count"] == 1
    info = skill_curator.record_usage("active-skill", base_dir=ws)
    assert info["use_count"] == 2

    # Ghim s3
    skill_curator.pin_skill("pinned-stale", pinned=True, base_dir=ws)

    # Giả lập thời gian cũ cho s2 và s3
    data = skill_curator.get_usage(base_dir=ws)
    old_time = int(time.time() - (40 * 86400))  # 40 ngày trước
    data["stale-skill"] = {"use_count": 1, "last_used_at": old_time, "pinned": False}
    data["pinned-stale"]["last_used_at"] = old_time
    skill_curator._save_data(data, base_dir=ws)

    # 2. Lưu trữ skill cũ
    archived = skill_curator.archive_stale_skills(ws_skills, stale_days=30, base_dir=ws)
    assert "stale-skill" in archived
    assert "pinned-stale" not in archived  # Pinned không bị lưu trữ
    assert "active-skill" not in archived  # Vừa dùng không bị lưu trữ
    assert not (ws_skills / "stale-skill").exists()
    assert (ws_skills / ".archive" / "stale-skill").exists()

    # 3. Khôi phục skill
    ok = skill_curator.restore_archived(ws_skills, "stale-skill", base_dir=ws)
    assert ok
    assert (ws_skills / "stale-skill").exists()
    assert not (ws_skills / ".archive" / "stale-skill").exists()


def test_skills_prompt_block_formatting(tmp_path: Path):
    d = tmp_path / "skill1"
    d.mkdir()
    (d / "SKILL.md").write_text("---\nname: my-skill\ndescription: This is a short description without dot\ncategory: dev\n---\nContent")
    from nestor.core.config import Config
    cfg = Config()
    s = skillmod.load_one(d, cfg)
    block = skillmod.prompt_block({"my-skill": s})
    assert 'category="dev"' in block
    assert "<name>my-skill</name>" in block
    assert "<description>This is a short description without dot.</description>" in block
