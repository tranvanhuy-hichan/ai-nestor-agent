"""Dung ket mot hoi thoai thanh Skill (SKILL.md) hoac Rule (mot dong quy tac) bang LLM."""
import hashlib
import os
import re
import tempfile
import threading

import yaml

from nestor.core import config as cfgmod
from nestor.services import rules, sessions, skills as skillmod
from nestor.services.providers import make_provider

MAX_CHARS = 14000


class DistillError(ValueError):
    pass


def transcript(sid: str) -> str:
    out = []
    for m in sessions.messages(sid):
        if m["role"] in ("user", "assistant") and m.get("content"):
            out.append(f"{'NGƯỜI DÙNG' if m['role'] == 'user' else 'TRỢ LÝ'}: {m['content'].strip()}")
        elif m["role"] == "tool" and m.get("content"):
            out.append(f"[kết quả tool] {m['content'][:300]}")
    text = "\n\n".join(out)
    return text[-MAX_CHARS:]


def _ask(prompt: str, provider: str | None = None) -> str:
    cfg = cfgmod.load()
    pcfg = cfg.providers.get(provider or cfg.default_provider)
    if not pcfg:
        raise DistillError("chưa cấu hình model nào")
    res = "".join(ev.get("text", "") for ev in make_provider(pcfg).stream([{"role": "user", "content": prompt}], tools=[]) if ev.get("type") == "delta")
    if not res.strip():
        raise DistillError("model không trả lời, hãy thử lại")
    return res.strip()


def slug(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", __import__("unicodedata").normalize("NFKD", name.lower().replace("đ", "d")).encode("ascii", "ignore").decode()).strip("-")
    return s[:40] or "ky-nang-moi"


SKILL_PROMPT = """Dưới đây là một cuộc trò chuyện giữa người dùng và trợ lý đã hoàn thành một công việc. Hãy đúc kết thành MỘT kỹ năng dùng lại được, viết bằng tiếng Việt tự nhiên để chuyên viên không biết lập trình vẫn đọc và sửa được.
Chỉ trả về nội dung Markdown (không bọc trong ```), theo đúng cấu trúc:
DESCRIPTION: <một câu: khi nào dùng kỹ năng này>
# <Tên kỹ năng>
## Khi nào dùng
## Các bước
(đánh số, cụ thể, nêu tool/file mẫu đã dùng)
## Mẫu và thông tin cần hỏi người dùng
## Lỗi đã gặp và cách tránh
Không bịa chi tiết không có trong cuộc trò chuyện.

CUỘC TRÒ CHUYỆN:
{t}"""
RULE_PROMPT = """Từ cuộc trò chuyện dưới đây, rút ra MỘT quy tắc ngắn (một câu tiếng Việt, mệnh lệnh, dưới 200 ký tự) mà trợ lý phải luôn tuân theo trong các lần sau, dựa trên yêu cầu cố định hoặc chỉnh sửa lặp lại của người dùng. Chỉ trả về đúng câu quy tắc.

CUỘC TRÒ CHUYỆN:
{t}"""


class DraftConflict(DistillError):
    pass


_draft_lock = threading.Lock()


def _transcript(sid: str) -> str:
    if not sessions.get(sid):
        raise DistillError("không có phiên này")
    text = transcript(sid)
    if not text.strip():
        raise DistillError("hội thoại chưa có nội dung để đúc kết")
    return text


def _workspace_file(cfg, skill):
    root = (cfg.workspace_path() / "skills").resolve()
    path = skill.path / "SKILL.md"
    return path if root in path.resolve().parents and not path.is_symlink() else None


def _revision(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()


def draft_skill(sid: str, name: str = "", provider: str | None = None) -> dict:
    text = _transcript(sid)
    md = re.sub(r"^```\w*\n|\n```$", "", _ask(SKILL_PROMPT.format(t=text), provider))
    desc_match = re.match(r"\s*DESCRIPTION:\s*(.+)\n", md)
    description, body = (desc_match[1].strip(), md[desc_match.end():].strip()) if desc_match else ("Kỹ năng đúc kết từ hội thoại", md)
    title = re.search(r"^#\s+(.+)$", body, re.M)
    name = slug(name or (title[1] if title else ""))
    cfg = cfgmod.load()
    words = set(name.split("-"))
    candidates = []
    for skill in skillmod.discover(cfg).values():
        if skill.name != name and len(words & set(skill.name.split("-"))) < 2:
            continue
        if path := _workspace_file(cfg, skill):
            content = path.read_text(encoding="utf-8", errors="replace")
            front, existing_body = skillmod.split_frontmatter(content)
            candidates.append({"name": skill.name, "description": str(front.get("description", "")),
                               "body": existing_body.strip(), "revision": _revision(content)})
    candidates.sort(key=lambda item: (item["name"] != name, item["name"]))
    return {"name": name, "description": description, "body": body, "matches": candidates[:5]}


def save_draft(name: str, description: str, body: str, revision: str | None = None) -> dict:
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) or len(name) > 80:
        raise DistillError("tên kỹ năng chỉ gồm chữ thường, số và dấu gạch ngang")
    if not description.strip() or not body.strip():
        raise DistillError("cần mô tả và nội dung kỹ năng")
    cfg = cfgmod.load()
    with _draft_lock:
        skills = skillmod.discover(cfg)
        existing = skills.get(name)
        root = (cfg.workspace_path() / "skills").resolve()
        directory = root / name
        created = False
        if revision is not None:
            path = _workspace_file(cfg, existing) if existing else None
            if not path:
                raise DraftConflict("kỹ năng đã thay đổi hoặc không thể sửa trong workspace")
            prior = path.read_text(encoding="utf-8", errors="replace")
            if _revision(prior) != revision:
                raise DraftConflict("kỹ năng đã thay đổi, hãy mở lại bản xem trước")
            front, _ = skillmod.split_frontmatter(prior)
        else:
            if existing:
                raise DraftConflict("tên kỹ năng đã tồn tại, hãy đổi tên hoặc chọn cập nhật")
            try:
                directory.mkdir(parents=True)
            except FileExistsError as exc:
                raise DraftConflict("thư mục kỹ năng đã tồn tại, hãy chọn tên khác") from exc
            created = True
            path = directory / "SKILL.md"
            front = {}
        tmp = None
        try:
            front.update(name=name, description=description.strip())
            content = f"---\n{yaml.safe_dump(front, allow_unicode=True, sort_keys=False)}---\n{body.strip()}\n"
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as handle:
                tmp = handle.name
                handle.write(content)
            os.replace(tmp, path)
        except OSError:
            if tmp:
                os.unlink(tmp)
            if created:
                directory.rmdir()
            raise
    return {"kind": "skill", "name": name, "description": description.strip(), "content": content}


def distill(sid: str, kind: str, name: str = "", provider: str | None = None) -> dict:
    if kind == "rule":
        text = _ask(RULE_PROMPT.format(t=_transcript(sid)), provider).splitlines()[0].strip(" -*\"'")
        return {"kind": "rule", **rules.add(text)}
    if kind != "skill":
        raise DistillError("kind phải là 'skill' hoặc 'rule'")
    draft = draft_skill(sid, name, provider)
    base = draft["name"]
    suffix = 1
    while True:
        try:
            return save_draft(draft["name"], draft["description"], draft["body"])
        except DraftConflict:
            suffix += 1
            draft["name"] = f"{base}-{suffix}"
