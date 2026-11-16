"""Quy tac ghi nho + dung ket hoi thoai thanh skill/rule."""
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..services import distill, rules

AUTO = True
router = APIRouter()


@router.get("/rules")
def list_rules():
    return rules.list_all()


class RuleBody(BaseModel):
    text: str


@router.post("/rules")
def add_rule(b: RuleBody):
    try:
        return rules.add(b.text)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e


@router.delete("/rules/{idx}")
def delete_rule(idx: int):
    if not rules.delete(idx):
        raise HTTPException(404, "không có quy tắc này")
    return {"ok": True}


class DistillBody(BaseModel):
    kind: Literal["skill", "rule"] = "skill"
    name: str = ""
    provider: str | None = None


@router.post("/sessions/{sid}/distill")
def distill_session(sid: str, b: DistillBody):
    try:
        return distill.distill(sid, b.kind, b.name, b.provider)
    except distill.DistillError as e:
        raise HTTPException(400, str(e)) from e
