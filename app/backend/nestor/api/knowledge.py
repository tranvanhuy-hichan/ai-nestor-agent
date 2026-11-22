"""Kho tài liệu: danh mục kiểu NotebookLM, mỗi danh mục chứa tài liệu riêng và có 1 phiên chat giới hạn đúng phạm vi đó."""
import mimetypes
from tempfile import TemporaryDirectory
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from starlette.background import BackgroundTask
from starlette.concurrency import run_in_threadpool

from ..core import config as cfgmod
from ..services import embeddings, jobs, knowledge, sessions
from ..services.office.preview import FORMATS, PreviewError, render_office_pdf

AUTO = True
router = APIRouter()


def _guard(fn, *a, **k):
    try:
        return fn(*a, **k)
    except knowledge.KnowledgeError as e:
        raise HTTPException(404 if "không có" in str(e) else 400, str(e)) from e


class NewCategory(BaseModel):
    name: str = ""
    icon: str = ""


class EditCategory(BaseModel):
    name: str | None = None
    icon: str | None = None


@router.get("/knowledge/categories")
def list_categories():
    return knowledge.list_categories()


@router.post("/knowledge/categories")
def create_category(b: NewCategory):
    return knowledge.create_category(b.name, b.icon)


@router.put("/knowledge/categories/{cid}")
def edit_category(cid: str, b: EditCategory):
    return _guard(knowledge.update_category, cid, b.name, b.icon)


@router.delete("/knowledge/categories/{cid}")
def delete_category(cid: str):
    return {"deleted": _guard(knowledge.delete_category, cid)}


class NotebookChatRequest(BaseModel):
    create: bool = False
    previous: list[str] = Field(default_factory=list, max_length=4)


@router.post("/knowledge/categories/{cid}/chat")
def category_chat(cid: str, body: NotebookChatRequest):
    cat = knowledge.get_category(cid)
    if not cat:
        raise HTTPException(404, "không có danh mục này")
    return {"id": sessions.category_chat(cid, cat["name"], create=body.create, previous=body.previous)}


@router.get("/knowledge")
def list_docs(category_id: str | None = None):
    cfg = cfgmod.load()
    e = None
    try:
        e = embeddings.get_embedder(cfg)
    except Exception:  # noqa: BLE001
        pass
    docs = knowledge.list_docs(category_id)
    counts = knowledge.vector_counts(e.model_id, category_id) if e else {}
    for doc in docs:
        doc["embedding_count"] = counts.get(doc["id"], 0)
    return {"docs": docs, "stats": knowledge.stats(category_id), "supported": sorted(knowledge.SUPPORTED), "semantic": e.kind if e else None}


@router.post("/knowledge/upload")
async def upload(name: str, request: Request, category_id: str | None = None):
    if int(request.headers.get("content-length") or 0) > knowledge.MAX_UPLOAD:
        raise HTTPException(413, "file quá lớn (tối đa 60MB)")
    data = bytearray()
    async for chunk in request.stream():
        if len(data) + len(chunk) > knowledge.MAX_UPLOAD:
            raise HTTPException(413, "file quá lớn (tối đa 60MB)")
        data.extend(chunk)
    try:
        return await run_in_threadpool(knowledge.add_bytes, name, data, category_id=category_id)
    except knowledge.KnowledgeError as e:
        raise HTTPException(400, str(e)) from e


class FolderBody(BaseModel):
    path: str
    category_id: str | None = None


@router.post("/knowledge/folder")
def add_folder(b: FolderBody):
    p = Path(b.path).expanduser()
    try:
        return knowledge.add_folder(p.resolve(), category_id=b.category_id)
    except (knowledge.KnowledgeError, OSError) as e:
        raise HTTPException(400, str(e)) from e


class SearchBody(BaseModel):
    query: str
    limit: int = 6
    category_id: str | None = None


@router.post("/knowledge/search")
def search(b: SearchBody):
    if not b.query.strip():
        raise HTTPException(400, "nhập nội dung cần tìm")
    return knowledge.search(b.query, b.limit, b.category_id)


class AnalyzeBody(BaseModel):
    focus: str = ""
    category_id: str | None = None


@router.post("/knowledge/analyze")
def analyze(b: AnalyzeBody):
    """Phân tích các tài liệu đã thêm và đề xuất phương án: chạy như một việc nền, kết quả xem ở trang Tác vụ."""
    if not knowledge.has_docs(b.category_id):
        raise HTTPException(400, "chưa có tài liệu nào sẵn sàng để phân tích")
    focus = b.focus.strip() or "Phân tích các tài liệu này và đề xuất phương án thực hiện."
    return {"id": jobs.start_background(focus[:2000], kind="analysis", title="Phân tích tài liệu: " + focus[:50], permission="readonly", kb_category_id=b.category_id)}


@router.delete("/knowledge/{did}")
def delete(did: str):
    if not knowledge.delete(did):
        raise HTTPException(404, "không có tài liệu này")
    return {"ok": True}


@router.post("/knowledge/{did}/ocr", status_code=202)
def start_ocr(did: str):
    return {"started": _guard(knowledge.retry_ocr, did)}


@router.get("/knowledge/{did}/ocr/{page}")
def read_ocr(did: str, page: int):
    if not knowledge.get(did):
        raise HTTPException(404, "không có tài liệu này")
    return {"words": knowledge.ocr_words(did, page)}


@router.get("/knowledge/{did}/passage")
def passage(did: str, loc: str, chunk_id: int | None = None):
    p = knowledge.passage(did, loc, chunk_id=chunk_id)
    if not p:
        raise HTTPException(404, "không có tài liệu này")
    return p


@router.get("/knowledge/{did}/chunks")
def doc_chunks(did: str, offset: int = Query(0, ge=0), loc: str | None = None, chunk_id: int | None = None):
    d = knowledge.get(did)
    if not d:
        raise HTTPException(404, "không có tài liệu này")
    return {"doc": d, "chunks": knowledge.doc_chunks(did, offset=offset, loc=loc, chunk_id=chunk_id)}



def original(did: str):
    d = knowledge.get(did)
    if not d or not d.get("path") or not Path(d["path"]).is_file():
        raise HTTPException(404, "không còn file gốc")
    return d


@router.get("/knowledge/{did}/preview")
def preview(did: str):
    return knowledge.text_preview(original(did))


@router.get("/knowledge/{did}/office-preview")
def office_preview(did: str):
    d = original(did)
    if d["ext"] not in FORMATS:
        raise HTTPException(415, "Định dạng này không phải tệp Office được hỗ trợ.")
    work = TemporaryDirectory(prefix="nestor-office-preview-")
    try:
        pdf = render_office_pdf(Path(d["path"]), d["ext"], Path(work.name))
        return FileResponse(
            pdf, media_type="application/pdf", background=BackgroundTask(work.cleanup),
            headers={"Cache-Control": "private, no-store", "X-Content-Type-Options": "nosniff"},
        )
    except PreviewError as exc:
        work.cleanup()
        raise HTTPException(422, str(exc)) from exc
    except BaseException:
        work.cleanup()
        raise


@router.get("/knowledge/{did}/file")
def file(did: str, inline: bool = False):
    d = original(did)
    mime = mimetypes.guess_type(d["name"])[0] or "application/octet-stream"
    safe_inline = mime in {
        "application/pdf", "image/png", "image/jpeg", "image/gif", "image/webp", "image/avif",
        "image/bmp", "text/plain", "audio/mpeg", "audio/wav", "audio/x-wav", "audio/ogg", "video/mp4", "video/webm",
    }
    return FileResponse(d["path"], media_type=mime, filename=Path(d["name"]).name,
                        content_disposition_type="inline" if inline and safe_inline else "attachment",
                        headers={"X-Content-Type-Options": "nosniff", "Content-Security-Policy": "sandbox"})
