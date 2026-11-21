"""API trang kieu Notion (file JSON block-doc trong workspace/pages)."""
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from ..services import pages, sessions

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
    content: dict[str, Any] | None = None
    icon: str = ""


class EditPage(BaseModel):
    title: str | None = None
    content: dict[str, Any] | None = None
    icon: str | None = None
    fullWidth: bool | None = None


class MovePage(BaseModel):
    parent: str = ""
    order: float | None = None


class NotebookChatRequest(BaseModel):
    create: bool = False
    previous: list[str] = Field(default_factory=list, max_length=4)


@router.get("/pages")
def list_pages():
    return pages.list_pages()


@router.get("/pages/search")
def search_pages(q: str = ""):
    return pages.search(q)


@router.post("/pages")
def create_page(b: NewPage):
    return _guard(pages.create, b.title, b.parent, b.content, b.icon)


class ImageUpload(BaseModel):
    data: str = Field(max_length=14_000_000)


@router.post("/pages/assets")
def upload_image(b: ImageUpload):
    return {"url": _guard(pages.save_image, b.data)}


@router.get("/pages/assets/{name}")
def get_image(name: str):
    return FileResponse(_guard(pages.image_path, name), headers={"X-Content-Type-Options": "nosniff"})


@router.get("/pages/{pid}")
def get_page(pid: str):
    return _guard(pages.get, pid)


@router.put("/pages/{pid}")
def edit_page(pid: str, b: EditPage):
    return _guard(pages.update, pid, b.title, b.content, b.icon, b.fullWidth)


@router.get("/pages/{pid}/export")
def export_page(pid: str):
    return {"markdown": _guard(pages.export_markdown, pid)}


@router.post("/pages/{pid}/chat")
def notebook_chat(pid: str, body: NotebookChatRequest):
    root = _guard(pages.notebook_root, pid)
    return {"id": sessions.notebook_chat(root["id"], root["title"], create=body.create, previous=body.previous)}


@router.post("/pages/{pid}/move")
def move_page(pid: str, b: MovePage):
    return _guard(pages.move, pid, b.parent, b.order)


@router.delete("/pages/{pid}")
def delete_page(pid: str):
    return {"deleted": _guard(pages.delete, pid)}
