"""API trang kieu Notion (file markdown trong workspace/pages)."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..services import pages

AUTO = True
router = APIRouter()


def _guard(fn, *a, **k):
    try:
        return fn(*a, **k)
    except pages.PageError as e:
        raise HTTPException(404 if "không có" in str(e) else 400, str(e)) from e


class NewPage(BaseModel):
    title: str = ""
    parent: str = ""
    content: str = ""
    icon: str = ""


class EditPage(BaseModel):
    title: str | None = None
    content: str | None = None
    icon: str | None = None


class MovePage(BaseModel):
    parent: str = ""
    order: float | None = None


@router.get("/pages")
def list_pages():
    return pages.list_pages()


@router.get("/pages/search")
def search_pages(q: str = ""):
    return pages.search(q)


@router.post("/pages")
def create_page(b: NewPage):
    return _guard(pages.create, b.title, b.parent, b.content, b.icon)


@router.get("/pages/{pid}")
def get_page(pid: str):
    return _guard(pages.get, pid)


@router.put("/pages/{pid}")
def edit_page(pid: str, b: EditPage):
    return _guard(pages.update, pid, b.title, b.content, b.icon)


@router.post("/pages/{pid}/move")
def move_page(pid: str, b: MovePage):
    return _guard(pages.move, pid, b.parent, b.order)


@router.delete("/pages/{pid}")
def delete_page(pid: str):
    return {"deleted": _guard(pages.delete, pid)}
