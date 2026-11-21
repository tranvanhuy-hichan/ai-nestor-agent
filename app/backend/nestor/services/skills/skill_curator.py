"""Hệ thống Quản lý và Bảo trì Vòng đời Kỹ năng (Skill Curator).

Học hỏi từ Hermes Agent Curator:
- Theo dõi tần suất và thời điểm sử dụng gần nhất của từng skill.
- Hỗ trợ ghim (pin) các skill quan trọng để không bao giờ bị lưu trữ.
- Tự động phát hiện và chuyển các skill tự sinh nhưng không dùng trong thời gian dài
  vào thư mục lưu trữ `.archive/`, giữ cho danh mục gọn gàng.
"""
from __future__ import annotations

import json
import logging
import shutil
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def _usage_file(base_dir: Path | None = None) -> Path:
    if base_dir:
        p = base_dir / ".nestor" / "skill_usage.json"
    else:
        p = Path.home() / ".config" / "nestor" / "skill_usage.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def _load_data(base_dir: Path | None = None) -> dict[str, Any]:
    f = _usage_file(base_dir)
    if not f.is_file():
        return {}
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except Exception as e:
        logger.warning("Không đọc được skill_usage.json: %s", e)
        return {}


def _save_data(data: dict[str, Any], base_dir: Path | None = None) -> None:
    f = _usage_file(base_dir)
    try:
        f.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        logger.error("Không ghi được skill_usage.json: %s", e)


def record_usage(skill_name: str, action: str = "read", base_dir: Path | None = None) -> dict:
    """Ghi nhận lượt sử dụng của một kỹ năng."""
    data = _load_data(base_dir)
    entry = data.get(skill_name, {
        "use_count": 0,
        "first_used_at": int(time.time()),
        "last_used_at": int(time.time()),
        "pinned": False,
        "state": "active",
    })
    entry["use_count"] = entry.get("use_count", 0) + 1
    entry["last_used_at"] = int(time.time())
    entry["state"] = "active"
    data[skill_name] = entry
    _save_data(data, base_dir)
    return entry


def get_usage(skill_name: str | None = None, base_dir: Path | None = None) -> dict:
    """Lấy số liệu sử dụng của tất cả hoặc một skill cụ thể."""
    data = _load_data(base_dir)
    if skill_name:
        return data.get(skill_name, {
            "use_count": 0,
            "pinned": False,
            "state": "active",
        })
    return data


def pin_skill(skill_name: str, pinned: bool = True, base_dir: Path | None = None) -> bool:
    """Ghim hoặc bỏ ghim một skill để bảo vệ không bị lưu trữ tự động."""
    data = _load_data(base_dir)
    entry = data.setdefault(skill_name, {
        "use_count": 0,
        "first_used_at": int(time.time()),
        "last_used_at": int(time.time()),
        "pinned": False,
        "state": "active",
    })
    entry["pinned"] = bool(pinned)
    _save_data(data, base_dir)
    return True


def archive_stale_skills(skills_dir: Path, stale_days: int = 30, base_dir: Path | None = None) -> list[str]:
    """Tự động chuyển các skill trong workspace không dùng quá stale_days vào thư mục .archive/."""
    if not skills_dir.is_dir():
        return []

    data = _load_data(base_dir)
    now = time.time()
    cutoff_time = now - (stale_days * 86400)
    archived = []

    archive_dir = skills_dir / ".archive"
    archive_dir.mkdir(parents=True, exist_ok=True)

    for skill_path in skills_dir.iterdir():
        if not skill_path.is_dir() or skill_path.name.startswith("."):
            continue

        skill_name = skill_path.name
        info = data.get(skill_name, {})

        # Không bao giờ lưu trữ nếu skill được ghim (pinned)
        if info.get("pinned"):
            continue

        last_used = info.get("last_used_at")
        # Nếu chưa dùng bao giờ hoặc dùng lần cuối trước cutoff
        if last_used and last_used < cutoff_time:
            target = archive_dir / skill_name
            if target.exists():
                shutil.rmtree(target)
            shutil.move(str(skill_path), str(target))
            info["state"] = "archived"
            info["archived_at"] = int(now)
            data[skill_name] = info
            archived.append(skill_name)

    if archived:
        _save_data(data, base_dir)
    return archived


def restore_archived(skills_dir: Path, skill_name: str, base_dir: Path | None = None) -> bool:
    """Khôi phục một skill từ thư mục .archive/ trở lại danh mục hoạt động."""
    target_archive = skills_dir / ".archive" / skill_name
    if not target_archive.is_dir():
        return False

    dest = skills_dir / skill_name
    if dest.exists():
        return False

    shutil.move(str(target_archive), str(dest))
    data = _load_data(base_dir)
    if skill_name in data:
        data[skill_name]["state"] = "active"
        data[skill_name]["last_used_at"] = int(time.time())
        _save_data(data, base_dir)
    return True
