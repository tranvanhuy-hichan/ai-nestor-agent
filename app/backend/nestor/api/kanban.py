"""API bang Kanban ca nhan: the 'viec can lam' + giao viec cho Nestor chay nen (tai dung jobs.py)."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..services import jobs, kanban

AUTO = True
router = APIRouter()


@router.get("/kanban")
def get_board():
    return kanban.board()


class NewCard(BaseModel):
    title: str
    body: str = ""
    role: str = ""


@router.post("/kanban")
def new_card(b: NewCard):
    if not b.title.strip():
        raise HTTPException(400, "thiếu tiêu đề")
    cid = kanban.create(b.title, b.body, b.role)
    return {"id": cid}


class UpdateCard(BaseModel):
    title: str | None = None
    body: str | None = None
    role: str | None = None


@router.patch("/kanban/{card_id}")
def edit_card(card_id: str, b: UpdateCard):
    if not kanban.get(card_id):
        raise HTTPException(404, "không có thẻ này")
    fields = {k: v for k, v in b.model_dump().items() if v is not None}
    kanban.update(card_id, **fields)
    return {"ok": True}


class Reorder(BaseModel):
    before_id: str | None = None


@router.post("/kanban/{card_id}/reorder")
def reorder_card(card_id: str, b: Reorder):
    if not kanban.get(card_id):
        raise HTTPException(404, "không có thẻ này")
    kanban.reorder(card_id, b.before_id)
    return {"ok": True}


@router.delete("/kanban/{card_id}")
def delete_card(card_id: str):
    if not kanban.delete(card_id):
        raise HTTPException(404, "không có thẻ này")
    return {"ok": True}


class Dispatch(BaseModel):
    permission: str = "default"
    provider: str | None = None


@router.post("/kanban/{card_id}/dispatch")
def dispatch_card(card_id: str, b: Dispatch):
    if b.permission not in ("default", "readonly", "guarded", "full"):
        raise HTTPException(400, "quyền không hợp lệ")
    try:
        return kanban.dispatch(card_id, b.permission, b.provider)
    except jobs.JobError as e:
        raise HTTPException(400, str(e)) from e


@router.post("/kanban/{card_id}/retry")
def retry_card(card_id: str):
    """The dang blocked (job that bai/bi huy): xoa lien ket job cu de giao lai tu dau."""
    card = kanban.get(card_id)
    if not card:
        raise HTTPException(404, "không có thẻ này")
    kanban.update(card_id, job_id=None)
    return {"ok": True}
