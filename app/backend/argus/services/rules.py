"""Quy tac ghi nho cua nguoi dung ("van ban cua phong luon ky thua lenh"): moi dong trong workspace/RULES.md, nap vao moi system prompt."""
from ..core import config as cfgmod

MAX_RULES = 50


def _file():
    return cfgmod.load().workspace_path() / "RULES.md"


def _lines() -> list[str]:
    try:
        return [ln[2:].strip() for ln in _file().read_text(encoding="utf-8").splitlines() if ln.startswith("- ") and ln[2:].strip()]
    except OSError:
        return []


def _write(rules: list[str]) -> None:
    f = _file()
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text("# Quy tắc của người dùng (luôn tuân theo)\n" + "".join(f"- {r}\n" for r in rules), encoding="utf-8")


def list_all() -> list[dict]:
    return [{"id": i, "text": t} for i, t in enumerate(_lines())]


def add(text: str) -> dict:
    text = " ".join((text or "").split())[:300]
    if not text:
        raise ValueError("quy tắc trống")
    rules = _lines()
    if text in rules:
        return {"id": rules.index(text), "text": text}
    if len(rules) >= MAX_RULES:
        raise ValueError(f"tối đa {MAX_RULES} quy tắc, hãy xóa bớt")
    _write(rules + [text])
    return {"id": len(rules), "text": text}


def delete(idx: int) -> bool:
    rules = _lines()
    if not 0 <= idx < len(rules):
        return False
    del rules[idx]
    _write(rules)
    return True
