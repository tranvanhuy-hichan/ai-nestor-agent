"""Quy tac ghi nho + dung ket hoi thoai thanh skill/rule."""
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

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



class SkillDraftRequest(BaseModel):
    name: str = Field("", max_length=120)
    provider: str | None = None


class SkillDraftSave(BaseModel):
    name: str = Field(max_length=80)
    description: str = Field(max_length=500)
    body: str = Field(max_length=100_000)
    revision: str | None = Field(None, min_length=64, max_length=64)


@router.post("/sessions/{sid}/skill-draft")
def draft_skill(sid: str, body: SkillDraftRequest):
    try:
        return distill.draft_skill(sid, body.name, body.provider)
    except distill.DistillError as exc:
        raise HTTPException(400, str(exc)) from exc


@router.post("/skills/draft/save")
def save_skill_draft(body: SkillDraftSave):
    try:
        return distill.save_draft(body.name, body.description, body.body, body.revision)
    except distill.DraftConflict as exc:
        raise HTTPException(409, str(exc)) from exc
    except distill.DistillError as exc:
        raise HTTPException(400, str(exc)) from exc
