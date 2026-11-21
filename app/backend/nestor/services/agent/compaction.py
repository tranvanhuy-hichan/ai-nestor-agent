"""Tom tat phan hoi thoai cu khi qua dai, de model nho (context ngan) khong quen dau cuoc tro chuyen."""
import json

from nestor.core.config import Config
from nestor.services import sessions
from nestor.services.providers import ProviderError, make_provider

PROMPT = ("Tóm tắt cuộc hội thoại dưới đây thành các ý chính để người trợ lý có thể tiếp tục công việc. "
          "Giữ nguyên: yêu cầu của người dùng, quyết định đã chốt, tên file và đường dẫn, kết quả quan trọng, việc còn dở. "
          "Tối đa 250 từ, viết gạch đầu dòng, không thêm lời dẫn.")


def _size(m: dict) -> int:
    return len(m.get("content", "")) + len(json.dumps(m.get("tool_calls", ""), ensure_ascii=False))


def _render(m: dict) -> str:
    if m["role"] == "tool":
        return f"[kết quả tool] {m['content'][:500]}"
    calls = "".join(f" [gọi {c['name']}({json.dumps(c['args'], ensure_ascii=False)[:150]})]" for c in m.get("tool_calls", []))
    return f"{'Người dùng' if m['role'] == 'user' else 'Trợ lý'}: {m['content'][:1500]}{calls}"


def plan(msgs: list[dict], limit: int, keep_turns: int = 2) -> int | None:
    """Tra ve chi so cat: tom tat msgs[:idx], giu lai phan con lai (bat dau tai mot tin nhan nguoi dung)."""
    if sum(_size(m) for m in msgs) <= limit:
        return None
    users = [i for i, m in enumerate(msgs) if m["role"] == "user"]
    if len(users) <= keep_turns:
        return None
    return users[-keep_turns]


def maybe_compact(sid: str, cfg: Config, provider_name: str, *, force: bool = False) -> bool:
    sess = sessions.get(sid)
    if not sess:
        return False
    msgs = sessions.messages(sid, after_id=sess["summary_upto"], with_ids=True)
    cut = plan(msgs, 0 if force else cfg.agent.compact_chars, keep_turns=1 if force else 2)
    if not cut:
        return False
    old = msgs[:cut]
    text = (f"Tóm tắt trước đó:\n{sess['summary']}\n\n" if sess["summary"] else "") + "\n".join(_render(m) for m in old)
    out = summarize(cfg, provider_name, text)
    if not out:
        return False
    return sessions.set_summary(sid, out, old[-1]["_id"], previous=sess["summary_upto"])


def summarize(cfg: Config, provider_name: str, text: str) -> str:
    try:
        return "".join(e["text"] for e in make_provider(cfg.providers[provider_name]).stream(
            [{"role": "system", "content": PROMPT}, {"role": "user", "content": text[:30000]}], []) if e["type"] == "delta").strip()
    except ProviderError:
        return ""


def highlights(sid: str, cfg: Config, provider_name: str) -> str:
    sess = sessions.get(sid)
    if not sess:
        return ""
    history = sessions.messages(sid, after_id=sess["summary_upto"])
    lines = [sess["summary"], *(_render(m) for m in history[-40:])]
    return summarize(cfg, provider_name, "\n".join(line for line in lines if line)) if history or sess["summary"] else ""
