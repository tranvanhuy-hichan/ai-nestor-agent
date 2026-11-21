"""Dung ket mot hoi thoai thanh Skill (SKILL.md) hoac Rule (mot dong quy tac) bang LLM."""
import re

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


def distill(sid: str, kind: str, name: str = "", provider: str | None = None) -> dict:
    if not sessions.get(sid):
        raise DistillError("không có phiên này")
    t = transcript(sid)
    if not t.strip():
        raise DistillError("hội thoại chưa có nội dung để đúc kết")
    cfg = cfgmod.load()
    if kind == "rule":
        text = _ask(RULE_PROMPT.format(t=t), provider).splitlines()[0].strip(" -*\"'")
        return {"kind": "rule", **rules.add(text)}
    if kind != "skill":
        raise DistillError("kind phải là 'skill' hoặc 'rule'")
    md = re.sub(r"^```\w*\n|\n```$", "", _ask(SKILL_PROMPT.format(t=t), provider))
    m = re.match(r"\s*DESCRIPTION:\s*(.+)\n", md)
    desc, body = (m.group(1).strip(), md[m.end():].strip()) if m else ("Kỹ năng đúc kết từ hội thoại", md)
    title = re.search(r"^#\s+(.+)$", body, re.M)
    sname = slug(name or (title.group(1) if title else ""))
    d = cfg.workspace_path() / "skills" / sname
    if d.exists():
        sname = f"{sname}-{len([p for p in d.parent.iterdir() if p.name.startswith(sname)]) + 1}"
    skillmod.create(cfg, sname, desc, body)
    return {"kind": "skill", "name": sname, "description": desc, "content": (cfg.workspace_path() / "skills" / sname / "SKILL.md").read_text(encoding="utf-8")}
