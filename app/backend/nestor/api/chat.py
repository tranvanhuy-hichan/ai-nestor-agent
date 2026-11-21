import json
import shutil
from typing import Literal

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from ..core import config as cfgmod
from ..services import assistants, chat_runner, compaction, sessions, tools, usage, workfiles

router = APIRouter()


@router.get("/sessions")
def list_sessions(q: str = ""):
    return [s for s in sessions.list_all(q=q) if s["source"] != "subagent"]  # phien cua agent con xem o trang Viec nen


class NewSession(BaseModel):
    title: str = "Hội thoại mới"
    assistant: str = ""


@router.post("/sessions")
def create_session(b: NewSession):
    if b.assistant and not assistants.get(b.assistant):
        raise HTTPException(400, "không có trợ lý này")
    sid = sessions.create(b.title)
    if b.assistant:
        sessions.set_assistant(sid, b.assistant)
    return {"id": sid}


@router.get("/sessions/{sid}")
def get_session(sid: str):
    s = sessions.get(sid)
    if not s:
        raise HTTPException(404, "không có phiên này")
    return {**s, "messages": sessions.messages(sid)}


@router.get("/sessions/{sid}/usage")
def session_usage(sid: str):
    """Token đã dùng trong phiên và ngữ cảnh còn lại của model đang dùng."""
    if not sessions.get(sid):
        raise HTTPException(404, "không có phiên này")
    return usage.session_usage(sid, cfgmod.load().providers)


class ContextAction(BaseModel):
    action: Literal["compact", "highlights"]
    provider: str | None = None
    note: str = Field("", max_length=4000)


@router.post("/sessions/{sid}/context")
def update_context(sid: str, body: ContextAction):
    with chat_runner.edit_idle_session(sid) as editable:
        if not editable:
            raise HTTPException(409, "Hãy đợi tác vụ hiện tại kết thúc")
        sess = sessions.get(sid)
        if not sess:
            raise HTTPException(404, "Không có phiên này")
        cfg = cfgmod.load()
        provider = body.provider if body.provider in cfg.providers else cfg.default_provider
        scope = sess.get("assistant_scope", "")
        profile = assistants.scoped_profile(sess.get("assistant"))
        if scope and (not profile or profile["scope_key"] != scope):
            raise HTTPException(409, "Hồ sơ của phiên này đã bị xóa")
        if body.action == "compact":
            if not compaction.maybe_compact(sid, cfg, provider, force=True):
                raise HTTPException(422, "Chưa có lượt cũ để tóm tắt hoặc mô hình chưa trả về bản tóm tắt")
            return {"ok": True}
        note = body.note.strip()
        if not note:
            return {"note": compaction.highlights(sid, cfg, provider)}
        tools.remember(tools.ToolContext(cfg.workspace_path(), profile_id=scope), note)
        return {"ok": True}


class Truncate(BaseModel):
    index: int


@router.post("/sessions/{sid}/truncate")
def truncate(sid: str, b: Truncate):
    """Xoa tu tin nhan thu `index` tro di (dung cho sua tin nhan / tao lai cau tra loi)."""
    if not sessions.get(sid):
        raise HTTPException(404, "không có phiên này")
    sessions.truncate_from(sid, max(0, b.index))
    return {"ok": True}


class Rename(BaseModel):
    title: str


class PinBody(BaseModel):
    pinned: bool = True


@router.patch("/sessions/{sid}")
def rename_session(sid: str, body: Rename):
    sessions.rename(sid, body.title)
    return {"ok": True}


class AssistantPick(BaseModel):
    assistant: str = ""


@router.put("/sessions/{sid}/assistant")
def set_session_assistant(sid: str, body: AssistantPick):
    """Chon hoac bo chon tro ly chuyen trach cua phien ('' = bo chon)."""
    if not sessions.get(sid):
        raise HTTPException(404, "không có phiên này")
    if body.assistant and not assistants.get(body.assistant):
        raise HTTPException(400, "không có trợ lý này")
    with chat_runner.edit_idle_session(sid) as editable:
        if not editable or not sessions.set_assistant(sid, body.assistant):
            raise HTTPException(409, "Hãy bắt đầu phiên mới để đổi hồ sơ.")
    return {"ok": True, "assistant": body.assistant}


@router.post("/sessions/{sid}/pin")
def pin_session(sid: str, body: PinBody):
    sessions.pin(sid, body.pinned)
    return {"ok": True}


@router.delete("/sessions/{sid}")
def delete_session(sid: str):
    sessions.delete(sid)
    shutil.rmtree(workfiles.session_dir(cfgmod.load(), sid), ignore_errors=True)  # thu muc lam viec cua phien
    return {"ok": True}


SSE_HEADERS = {"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}


def _sse(ev: dict) -> str:
    return ": ping\n\n" if ev["type"] == "ping" else f"data: {json.dumps(ev, ensure_ascii=False)}\n\n"


class ChatBody(BaseModel):
    text: str
    session: str | None = None
    provider: str | None = None
    attachments: list[str] = []
    permission: Literal["default", "readonly", "guarded", "full", "plan"] = "default"
    effort: Literal["auto", "low", "medium", "high", "thinking"] = "auto"
    docs: bool = False  # "Hỏi từ tài liệu": chỉ trả lời dựa trên kho tài liệu, có nguồn
    temperature: float | None = None
    max_tokens: int | None = None
    assistant: str | None = None  # id tro ly chuyen trach (services/assistants.py)
    context: str = Field("", max_length=4000)  # ngu canh giao dien them vao system prompt (vd trang dang mo)


def _context(ctx: str) -> str:
    """Giao dien chi gui nhan ngu canh ('page:<ma>'); noi dung that do backend dung, khong nhan van ban tuy y."""
    kind, _, pid = ctx.partition(":")
    if kind in ("page", "page-draft"):
        from ..services import pages
        return pages.chat_context(pid.strip(), draft=kind == "page-draft")
    if kind == "kb-category":
        from ..services import knowledge
        return knowledge.category_chat_context(pid.strip())
    return ""


def _kb_category(ctx: str) -> str | None:
    kind, _, cid = ctx.partition(":")
    return cid.strip() if kind == "kb-category" and cid.strip() else None


@router.post("/chat")
def chat(body: ChatBody):
    stored = (sessions.get(body.session) or {}).get("assistant") if body.session else ""
    eff = body.assistant if body.assistant is not None else stored  # khong gui thi dung tro ly da luu cua phien
    draft = body.context.startswith("page-draft:")
    kb_category_id = _kb_category(body.context)
    tool_allow = assistants.tool_allow(eff)
    if draft:
        page_tools = {"page_read", "page_list", "page_search"}
        tool_allow = sorted(page_tools if tool_allow is None else page_tools.intersection(tool_allow))

    def gen():
        for ev in chat_runner.stream_chat(body.session, body.text, body.provider, attachments=body.attachments, permission="readonly" if draft else body.permission,
                                            effort=None if body.effort == "auto" else body.effort, docs=body.docs or bool(kb_category_id),
                                            temperature=body.temperature, max_tokens=body.max_tokens, detach=True,
                                            system_extra="\n\n".join(x for x in (assistants.prompt_for(eff), _context(body.context)) if x), tool_allow=tool_allow, assistant=body.assistant,
                                            kb_category_id=kb_category_id):
            yield _sse(ev)

    return StreamingResponse(gen(), media_type="text/event-stream", headers=SSE_HEADERS)


@router.get("/sessions/{sid}/run")
def run_state(sid: str):
    """Phiên có đang chạy agent không (giao diện dùng để nối lại sau khi đổi trang)."""
    return chat_runner.state(sid)


@router.get("/sessions/{sid}/attach")
def attach(sid: str, start: int = 0, run_id: str | None = None):
    """Replay a particular run so a stale cursor cannot attach to its successor."""
    run = chat_runner.lookup_run(sid, run_id)
    if run_id and not run:
        raise HTTPException(409, "luồng hội thoại đã kết thúc hoặc được thay thế")
    if run and start > len(run.events):
        raise HTTPException(409, "vị trí nối lại không hợp lệ")

    def gen():
        events = run.tail(max(0, start)) if run else ({"type": "done"},)
        for ev in events:
            yield _sse(ev)

    return StreamingResponse(gen(), media_type="text/event-stream", headers=SSE_HEADERS)


@router.post("/sessions/{sid}/stop")
def stop_run(sid: str, run_id: str | None = None):
    return {"ok": chat_runner.stop(sid, run_id)}


class Approval(BaseModel):
    ok: bool


@router.post("/approvals/{aid}")
def approve(aid: str, body: Approval):
    return {"ok": chat_runner.resolve_approval(aid, body.ok)}


class Answer(BaseModel):
    answer: str


@router.post("/questions/{qid}")
def answer_question(qid: str, body: Answer):
    return {"ok": chat_runner.answer_question(qid, body.answer)}


@router.get("/sessions/{sid}/checkpoint")
def checkpoint_state(sid: str):
    from ..services import checkpoints
    return {"files": checkpoints.last(sid)}


@router.post("/sessions/{sid}/undo")
def undo_last_turn(sid: str):
    """Hoàn tác các file agent đã ghi/sửa trong lượt gần nhất (không gồm thay đổi do lệnh shell)."""
    from ..services import checkpoints
    if chat_runner.active(sid):
        raise HTTPException(409, "agent đang chạy, hãy dừng rồi hoàn tác")
    return {"restored": checkpoints.undo(sid)}
