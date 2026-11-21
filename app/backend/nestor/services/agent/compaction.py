"""Tom tat phan hoi thoai cu khi qua dai, de model nho (context ngan) khong quen dau cuoc tro chuyen."""
import json

from nestor.core.config import Config
from nestor.services import sessions
from nestor.services.providers import ProviderError, make_provider

from .truncation import truncate_middle

SUMMARY_INPUT_CHARS = 30_000
PREVIOUS_SUMMARY_CHARS = 6_000

PROMPT = ("Tóm tắt cuộc hội thoại dưới đây thành các ý chính để người trợ lý có thể tiếp tục công việc. "
          "Giữ nguyên: yêu cầu và ràng buộc của người dùng, quyết định đã chốt, tên file và đường dẫn, lỗi nguyên văn, kết quả quan trọng, việc còn dở. "
          "Giữ message_id của kết quả công cụ quan trọng để đọc lại bằng tool_result_read khi cần. "
          "Tối đa 250 từ, viết gạch đầu dòng, không thêm lời dẫn.")


def _size(m: dict) -> int:
    return len(m.get("content", "")) + len(json.dumps(m.get("tool_calls", ""), ensure_ascii=False))


def _render(m: dict) -> str:
    if m["role"] == "tool":
        reference = f" message_id={m['_id']}" if m.get("_id") else ""
        preview = truncate_middle(m["content"], 500, marker="\n[…]\n")
        return f"[kết quả tool{reference}] {preview}"
    calls = "".join(f" [gọi {c['name']}({json.dumps(c['args'], ensure_ascii=False)[:150]})]" for c in m.get("tool_calls", []))
    preview = truncate_middle(m["content"], 1_500, marker="\n[…]\n")
    return f"{'Người dùng' if m['role'] == 'user' else 'Trợ lý'}: {preview}{calls}"


def plan(msgs: list[dict], limit: int, keep_turns: int = 2) -> int | None:
    """Tra ve chi so cat: tom tat msgs[:idx], giu lai phan con lai (bat dau tai mot tin nhan nguoi dung)."""
    if sum(_size(m) for m in msgs) <= limit:
        return None
    users = [i for i, m in enumerate(msgs) if m["role"] == "user"]
    if len(users) <= keep_turns:
        return None
    return users[-keep_turns]


def _batch(previous: str, messages: list[dict]) -> tuple[str, int]:
    """Build one bounded summary request and return the number of messages it covers."""
    if previous:
        previous = truncate_middle(previous, PREVIOUS_SUMMARY_CHARS, marker="\n[… Tóm tắt trước đó đã rút gọn …]\n")
    prefix = f"Tóm tắt trước đó:\n{previous}\n\n" if previous else ""
    budget = SUMMARY_INPUT_CHARS - len(prefix)
    lines = []
    size = 0
    boundary = 0
    for index, message in enumerate(messages):
        if message["role"] == "user" and index:
            boundary = index
            if size > budget:
                break
        line = _render(message)
        if size + len(line) > budget and boundary:
            return prefix + "\n".join(lines[:boundary]), boundary
        lines.append(line)
        size += len(line) + 1

    if size <= budget + 1:
        return prefix + "\n".join(lines), len(lines)

    # A single oversized turn cannot be split at a user boundary.
    marker = "\n[… Lượt quá dài. Có thể tìm lại nguyên văn trong lịch sử phiên …]\n"
    preview = truncate_middle("\n".join(lines), budget - len(marker), marker=marker)
    return prefix + preview, len(lines)


def maybe_compact(sid: str, cfg: Config, provider_name: str, *, force: bool = False) -> bool:
    sess = sessions.get(sid)
    if not sess:
        return False
    msgs = sessions.messages(sid, after_id=sess["summary_upto"], with_ids=True)
    cut = plan(msgs, 0 if force else cfg.agent.compact_chars, keep_turns=1 if force else 2)
    if not cut:
        return False
    text, covered = _batch(sess["summary"], msgs[:cut])
    out = summarize(cfg, provider_name, text)
    if not out:
        return False
    return sessions.set_summary(sid, out, msgs[covered - 1]["_id"], previous=sess["summary_upto"])


def summarize(cfg: Config, provider_name: str, text: str) -> str:
    try:
        return "".join(e["text"] for e in make_provider(cfg.providers[provider_name]).stream(
            [{"role": "system", "content": PROMPT}, {"role": "user", "content": text}], []) if e["type"] == "delta").strip()
    except ProviderError:
        return ""


def highlights(sid: str, cfg: Config, provider_name: str) -> str:
    sess = sessions.get(sid)
    if not sess:
        return ""
    history = sessions.messages(sid, after_id=sess["summary_upto"], with_ids=True)
    if not history and not sess["summary"]:
        return ""
    text = "\n".join(filter(None, [sess["summary"], *(_render(m) for m in history[-40:])]))
    marker = "\n[… Một phần lịch sử đã lược bớt …]\n"
    text = truncate_middle(text, SUMMARY_INPUT_CHARS - len(marker), marker=marker)
    return summarize(cfg, provider_name, text)
