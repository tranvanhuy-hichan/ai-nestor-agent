"""Trang thai to cong tac da agent (cap nhat song)."""
from fastapi import APIRouter, HTTPException

from ..services import teams

AUTO = True
router = APIRouter()


@router.get("/teams")
def list_teams():
    return teams.list_all()


@router.get("/teams/{tid}/status")
def team_status(tid: str):
    t = teams.get(tid)
    if not t:
        raise HTTPException(404, "không có tổ công tác này")
    return t


@router.get("/sessions/{sid}/team")
def session_team(sid: str):
    return teams.latest_for_session(sid) or {"members": []}
