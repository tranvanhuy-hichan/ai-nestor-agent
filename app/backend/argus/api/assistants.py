"""Tro ly chuyen trach (dung san + tu tao)."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..services import assistants

AUTO = True
router = APIRouter()


class AssistantBody(BaseModel):
    name: str
    prompt: str
    icon: str = "bot"
    group: str = "doanh-nghiep"
    description: str = ""
    starters: list[str] = []
    skills: list[str] = []
    tools: list[str] | None = None
    done_criteria: list[str] = []
    deliverables: list[str] = []


@router.get("/assistants")
def list_assistants():
    return assistants.list_all()


def _do(fn, *a):
    try:
        return fn(*a)
    except assistants.AssistantError as e:
        raise HTTPException(400, str(e)) from e


@router.post("/assistants/{aid}")
def create_assistant(aid: str, b: AssistantBody):
    return _do(assistants.save, aid, b.model_dump(), True)


@router.put("/assistants/{aid}")
def update_assistant(aid: str, b: AssistantBody):
    return _do(assistants.save, aid, b.model_dump(), False)


@router.delete("/assistants/{aid}")
def delete_assistant(aid: str):
    _do(assistants.delete, aid)
    return {"ok": True}
