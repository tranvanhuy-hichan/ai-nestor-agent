"""Hooks kieu Claude Code: chay lenh shell cua nguoi dung truoc/sau moi tool.

Cau hinh (gop theo thu tu): <workspace>/hooks.json, <du an>/.nestor/hooks.json
  {"PreToolUse": [{"matcher": "exec|write", "command": "./check.sh", "timeout": 30}],
   "PostToolUse": [{"matcher": "edit", "command": "ruff format ."}]}
Lenh nhan JSON {event, tool, args, result?} qua stdin. PreToolUse thoat voi ma 2 = CHAN tool, stderr duoc gui lai cho model.
"""
import json
import re
import subprocess
from pathlib import Path

EVENTS = ("PreToolUse", "PostToolUse")


def _load(path: Path) -> dict:
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def load(ctx) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {e: [] for e in EVENTS}
    files = [ctx.workspace / "hooks.json"]
    if ctx.project:
        files.append(Path(ctx.project) / ".nestor" / "hooks.json")
    for f in files:
        data = _load(f)
        for e in EVENTS:
            for h in data.get(e) or []:
                if isinstance(h, dict) and isinstance(h.get("command"), str) and h["command"].strip():
                    out[e].append(h)
    return out


def _matches(h: dict, tool: str) -> bool:
    m = h.get("matcher") or "*"
    if m == "*":
        return True
    try:
        return re.fullmatch(m, tool) is not None
    except re.error:
        return False


def run(ctx, event: str, tool: str, args: dict, result: str = "") -> str | None:
    """Chay cac hook khop. Tra ve ly do chan (chi PreToolUse, ma thoat 2) hoac None."""
    hs = [h for h in load(ctx)[event] if _matches(h, tool)]
    if not hs:
        return None
    payload = json.dumps({"event": event, "tool": tool, "args": args, "result": result[:4000], "cwd": str(ctx.workdir)}, ensure_ascii=False)
    for h in hs:
        try:
            p = subprocess.run(h["command"], shell=True, input=payload, capture_output=True, text=True, cwd=ctx.workdir,
                               timeout=min(int(h.get("timeout") or 30), 120))
        except (subprocess.TimeoutExpired, OSError, ValueError):
            continue
        if event == "PreToolUse" and p.returncode == 2:
            return (p.stderr or p.stdout or "hook chặn tool này").strip()[:1000]
    return None
