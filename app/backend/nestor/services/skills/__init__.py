"""Doc, kiem tra dieu kien, cai dat skill theo dinh dang SKILL.md cua ClawHub (frontmatter + metadata)."""
import io
import json
import os
import shutil
import stat
import sys
import tempfile

skills = sys.modules[__name__]
sys.modules[f"{__name__}.skills"] = skills
import time
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from nestor.core.config import Config

META_KEYS = ("openclaw", "clawdbot", "clawdis", "hermes")  # ho tro ClawHub + Hermes Agent skills format
MAX_DEPTH = 6
MAX_ZIP_FILES, MAX_ZIP_BYTES = 500, 20 * 1024 * 1024
OS_ALIAS = {"darwin": "darwin", "macos": "darwin", "linux": "linux", "win32": "win32", "windows": "win32"}


class SkillError(Exception):
    pass


def split_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    parts = text.split("\n---", 1)
    if len(parts) < 2:
        return {}, text
    head, body = parts[0][3:], parts[1].lstrip("-").lstrip("\n")
    try:
        front = yaml.safe_load(head) or {}
    except yaml.YAMLError:
        front = {}
        for line in head.strip().splitlines():
            k, _, v = line.partition(":")
            if k.strip():
                front[k.strip()] = v.strip()
    if not isinstance(front, dict):
        front = {}
    meta = front.get("metadata")
    if isinstance(meta, str):
        try:
            meta = json.loads(meta)
        except json.JSONDecodeError:
            try:
                meta = yaml.safe_load(meta)
            except yaml.YAMLError:
                meta = {}
    front["metadata"] = meta if isinstance(meta, dict) else {}
    return front, body


@dataclass
class Skill:
    name: str
    description: str
    path: Path
    body: str
    front: dict
    meta: dict
    enabled: bool = True
    missing: list[str] = field(default_factory=list)
    origin: dict | None = None
    bundled: bool = False  # skill di kem Nestor (chi doc); chi tro ly chuyen trach nap, khong dua vao danh sach skill chung
    category: str = "general"

    @property
    def eligible(self) -> bool:
        return not self.missing

    @property
    def active(self) -> bool:
        return self.enabled and self.eligible

    def instructions(self) -> str:
        return self.body.replace("{baseDir}", str(self.path))

    def to_dict(self) -> dict:
        return {
            "name": self.name, "description": self.description, "path": str(self.path),
            "enabled": self.enabled, "eligible": self.eligible, "missing": self.missing,
            "emoji": self.meta.get("emoji") or "", "homepage": self.front.get("homepage") or "",
            "primary_env": self.meta.get("primaryEnv") or "", "origin": self.origin,
            "requires": self.meta.get("requires") or {},
            "model_invocable": not self.front.get("disable-model-invocation", False), "bundled": self.bundled,
            "category": self.category,
        }


def _gate(meta: dict, cfg: Config, name: str) -> list[str]:
    entry = cfg.skills.get(name)
    missing: list[str] = []
    oses = meta.get("os")
    if oses:
        oses = [oses] if isinstance(oses, str) else oses
        if sys.platform.replace("linux2", "linux") not in {OS_ALIAS.get(o.lower(), o) for o in oses}:
            return [f"os:{'/'.join(oses)}"]
    if meta.get("always"):
        return []
    req = meta.get("requires") or {}
    missing += [f"bin:{b}" for b in req.get("bins", []) if not shutil.which(b)]
    any_bins = req.get("anyBins", [])
    if any_bins and not any(shutil.which(b) for b in any_bins):
        missing.append("anyBin:" + "|".join(any_bins))
    for var in req.get("env", []):
        provided = var in os.environ or (entry and (entry.env.get(var) or (meta.get("primaryEnv") == var and entry.api_key)))
        if not provided:
            missing.append(f"env:{var}")
    missing += [f"config:{c}" for c in req.get("config", [])]  # khong the dap ung (cau hinh rieng cua ung dung khac, Nestor khong co)
    return missing


def _find_skill_dirs(root: Path, depth: int = 0):
    if not root.is_dir() or depth > MAX_DEPTH:
        return
    if (root / "SKILL.md").is_file():
        yield root
        return
    for child in sorted(root.iterdir()):
        if child.is_dir() and not child.name.startswith("."):
            yield from _find_skill_dirs(child, depth + 1)


CATEGORY_MAP = {
    "autonomous-ai-agents": "agents",
    "software-development": "dev",
    "web-development": "dev",
    "web": "dev",
    "devops": "devops",
    "mlops": "devops",
    "security": "security",
    "productivity": "productivity",
    "note-taking": "productivity",
    "creative": "creative",
    "media": "creative",
    "research": "research",
    "data-science": "research",
    "finance": "finance",
    "payments": "finance",
    "blockchain": "finance",
    "social-media": "communication",
    "communication": "communication",
    "email": "communication",
    "apple": "communication",
    "mcp": "tools",
    "gaming": "creative",
    "health": "productivity",
    "smart-home": "tools",
    "dogfood": "dev",
}

VALID_CATEGORIES = {
    "agents", "dev", "devops", "security", "productivity",
    "creative", "research", "finance", "communication", "tools", "general",
}


def resolve_category(d: Path, front: dict, name: str) -> str:
    raw = front.get("category")
    if raw and isinstance(raw, str):
        c = raw.strip().lower()
        if c in CATEGORY_MAP:
            return CATEGORY_MAP[c]
        if c in VALID_CATEGORIES:
            return c
    parts = d.parts
    if "hermes" in parts:
        try:
            idx = parts.index("hermes")
            if idx + 1 < len(parts) - 1:
                folder_cat = parts[idx + 1].lower()
                return CATEGORY_MAP.get(folder_cat, "general")
        except Exception:
            pass
    nl = name.lower()
    if nl in ("excel-xlsx", "word-docx", "daily-planner", "meeting-notes", "career-coach", "study-coach", "cv-phong-van"):
        return "productivity"
    if nl in ("email-writer", "youtube-watcher"):
        return "communication"
    if nl in ("humanizer",):
        return "creative"
    return "general"


def load_one(d: Path, cfg: Config) -> Skill:
    front, body = split_frontmatter((d / "SKILL.md").read_text(errors="replace"))
    meta = next((front["metadata"][k] for k in META_KEYS if isinstance(front["metadata"].get(k), dict)), {})
    name = str(front.get("name") or d.name)
    entry = cfg.skills.get(name)
    origin = None
    if (d / ".clawhub" / "origin.json").is_file():
        try:
            origin = json.loads((d / ".clawhub" / "origin.json").read_text())
        except json.JSONDecodeError:
            pass
    category = resolve_category(d, front, name)
    return Skill(name=name, description=str(front.get("description") or "").strip(), path=d, body=body.strip(), front=front, meta=meta,
                 enabled=entry.enabled if entry else True, missing=_gate(meta, cfg, name), origin=origin, category=category)


BUNDLED_DIR = Path(__file__).resolve().parents[2] / "bundled_skills"


def discover(cfg: Config) -> dict[str, Skill]:
    skills: dict[str, Skill] = {}
    # 1. Kỹ năng trong workspace của người dùng (ưu tiên cao nhất)
    ws_skills = cfg.workspace_path() / "skills"
    for d in _find_skill_dirs(ws_skills):
        try:
            s = load_one(d, cfg)
        except OSError:
            continue
        skills.setdefault(s.name, s)

    # 2. Kỹ năng mẫu trong template đi kèm bản build (dự phòng nếu workspace chưa seed)
    try:
        from nestor.core.workspace import template_dir
        tpl_skills = template_dir() / "skills"
        if tpl_skills.is_dir() and tpl_skills.resolve() != ws_skills.resolve():
            for d in _find_skill_dirs(tpl_skills):
                try:
                    s = load_one(d, cfg)
                except OSError:
                    continue
                skills.setdefault(s.name, s)
    except Exception:
        pass

    # 3. Kỹ năng nghiệp vụ văn phòng đi kèm (bundled)
    for d in _find_skill_dirs(BUNDLED_DIR):  # skill di kem: skill cung ten trong workspace thang
        try:
            s = load_one(d, cfg)
        except OSError:
            continue
        s.bundled = True
        skills.setdefault(s.name, s)
    return skills


def env_for(skills: dict[str, Skill], cfg: Config) -> dict[str, str]:
    """Bien moi truong skill khai bao, chi cua skill dang bat va du dieu kien."""
    env: dict[str, str] = {}
    for s in skills.values():
        entry = cfg.skills.get(s.name)
        if s.active and entry:
            env.update({k: v for k, v in entry.env.items() if v})
            if s.meta.get("primaryEnv") and entry.api_key:
                env[s.meta["primaryEnv"]] = entry.api_key
    return env


def prompt_block(skills: dict[str, Skill], limit: int = 40000, bundled_limit: int = 18000) -> str:
    """Danh sach muc luc skill theo chuan Progressive Disclosure cua Hermes Agent.
    Cap do 0: chi hien name, category va mo ta ngan (< 80 ky tu, co dau cham) de tiet kiem token.
    Cap do 1: agent chu dong goi tool `skills_read(name)` de nap huong dan chi tiet khi can."""
    usable = [s for s in skills.values() if s.active and not s.front.get("disable-model-invocation")]
    own, bundled = [s for s in usable if not s.bundled], [s for s in usable if s.bundled]

    def _fmt(s: Skill, max_len: int = 80) -> str:
        first_line = s.description.strip().splitlines()[0] if s.description else ""
        desc = first_line[:max_len].strip()
        if desc and not desc.endswith((".", "!", "?")):
            desc += "."
        cat = getattr(s, "category", "general") or "general"
        return f'  <skill category="{cat}"><name>{s.name}</name><description>{desc}</description></skill>'

    lines, size = [], 0
    for s in own:
        line = _fmt(s, max_len=80)
        if size + len(line) > limit:
            lines.append("  <!-- Cac skill khac xem them qua skills_read -->")
            break
        lines.append(line)
        size += len(line)
    blines, bsize = [], 0
    for s in bundled:
        line = _fmt(s, max_len=75)
        if bsize + len(line) > bundled_limit:
            break
        blines.append(line)
        bsize += len(line)
    if not lines and not blines:
        return ""
    return ("## KIẾN THỨC CHUYÊN BIỆT (SKILLS - PROGRESSIVE DISCLOSURE)\n"
            "Hệ thống có sẵn các gói kỹ năng quy trình chuẩn dưới đây. Khi yêu cầu của người dùng khớp rõ ràng với một kỹ năng, "
            "hãy gọi tool `skills_read(name='...')` để nạp hướng dẫn TRƯỚC KHI làm (khong can nguoi dung chon skill). "
            "Sau khi đọc, hãy làm đúng theo từng bước hướng dẫn trong skill đó.\n<available_skills>\n" + "\n".join([*lines, *blines]) + "\n</available_skills>")


# ---------- cai dat / go bo
def _safe_extract(data: bytes, dest: Path) -> None:
    try:
        z = zipfile.ZipFile(io.BytesIO(data))
    except zipfile.BadZipFile as e:
        raise SkillError("file tải về không phải zip hợp lệ") from e
    infos = [i for i in z.infolist() if not i.is_dir()]
    if len(infos) > MAX_ZIP_FILES or sum(i.file_size for i in infos) > MAX_ZIP_BYTES:
        raise SkillError("skill quá lớn (tối đa 500 file / 20MB)")
    names = [i.filename for i in infos]
    prefix = ""
    if "SKILL.md" not in names:
        tops = {n.split("/", 1)[0] for n in names}
        if len(tops) == 1 and f"{next(iter(tops))}/SKILL.md" in names:
            prefix = next(iter(tops)) + "/"
        else:
            raise SkillError("zip không có SKILL.md")
    root = dest.resolve()
    for i in infos:
        rel = i.filename[len(prefix):]
        target = (dest / rel).resolve()
        if root not in target.parents:  # chong zip-slip
            raise SkillError(f"đường dẫn nguy hiểm trong zip: {i.filename}")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(z.read(i))
        if target.read_bytes()[:2] == b"#!":
            target.chmod(target.stat().st_mode | stat.S_IXUSR)


def install_zip(cfg: Config, data: bytes, slug: str, origin: dict) -> Skill:
    skills_dir = cfg.workspace_path() / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    target = skills_dir / slug
    if target.exists() and not origin.get("overwrite"):
        prev = (target / ".clawhub" / "origin.json")
        owner = json.loads(prev.read_text()).get("owner") if prev.is_file() else None
        if owner != origin.get("owner"):
            raise SkillError(f"đã có skill '{slug}' (không cùng tác giả). Xóa nó trước khi cài.")
    tmp = Path(tempfile.mkdtemp(prefix=".install-", dir=skills_dir))
    try:
        _safe_extract(data, tmp)
        (tmp / ".clawhub").mkdir(exist_ok=True)
        (tmp / ".clawhub" / "origin.json").write_text(json.dumps({**{k: v for k, v in origin.items() if k != "overwrite"}, "installedAt": int(time.time() * 1000)}))
        if target.exists():
            shutil.rmtree(target)
        tmp.rename(target)
    except Exception:
        shutil.rmtree(tmp, ignore_errors=True)
        raise
    return load_one(target, cfg)


def remove(cfg: Config, name: str) -> None:
    skills_dir = (cfg.workspace_path() / "skills").resolve()
    s = discover(cfg).get(name)
    if not s:
        raise SkillError(f"không có skill '{name}'")
    path = s.path.resolve()
    if skills_dir not in path.parents:
        raise SkillError("chỉ xóa được skill nằm trong workspace/skills")
    shutil.rmtree(path)


def create(cfg: Config, name: str, description: str, body: str) -> Skill:
    d = cfg.workspace_path() / "skills" / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "SKILL.md").write_text(f"---\nname: {name}\ndescription: {json.dumps(description, ensure_ascii=False)}\n---\n{body}\n")
    return load_one(d, cfg)


def patch(cfg: Config, name: str, old: str, new: str) -> Skill:
    """Sửa một đoạn trong SKILL.md theo kiểu patch (diff-based) của Hermes thay vì ghi đè cả file."""
    s = discover(cfg).get(name)
    if not s:
        raise SkillError(f"không tìm thấy skill '{name}'")
    skill_file = s.path / "SKILL.md"
    if not skill_file.is_file():
        raise SkillError(f"skill '{name}' không có file SKILL.md")
    content = skill_file.read_text(encoding="utf-8", errors="replace")
    if old not in content:
        raise SkillError(f"không tìm thấy đoạn cũ trong SKILL.md của '{name}'")
    if content.count(old) > 1:
        raise SkillError(f"đoạn cũ xuất hiện {content.count(old)} lần, hãy cung cấp đoạn văn bản dài hơn để khớp duy nhất 1 lần")
    skill_file.write_text(content.replace(old, new, 1), encoding="utf-8")
    return load_one(s.path, cfg)
