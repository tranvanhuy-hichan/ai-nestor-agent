"""Trang kieu Notion: moi trang la mot file JSON trong workspace/pages/<id>.json, chua meta (tieu de, trang cha, thu tu)
va content la mot TipTap/ProseMirror doc. Dung file thuong de agent doc/ghi duoc bang tool, nguoi dung van so huu du lieu."""
import base64
import binascii
import json
import re
import threading
import time
import uuid
from pathlib import Path
from typing import Any

from nestor.core import config as cfgmod
from nestor.core.text import fold

from . import blocktree

ID_RE = re.compile(r"^[a-f0-9]{10}$")
MAX_CONTENT = 2_000_000
_lock = threading.RLock()


class PageError(ValueError):
    pass


def _dir() -> Path:
    d = cfgmod.load().workspace_path() / "pages"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _path(pid: str) -> Path:
    if not ID_RE.match(pid or ""):
        raise PageError("mã trang không hợp lệ")
    return _dir() / f"{pid}.json"


def _info(pid: str, meta: dict) -> dict:
    return {"id": pid, "title": meta.get("title") or "Chưa đặt tên", "parent": meta.get("parent", ""), "icon": meta.get("icon", ""),
            "order": float(meta.get("order") or 0), "created": float(meta.get("created") or 0), "updated": float(meta.get("updated") or 0),
            "fullWidth": bool(meta.get("fullWidth", False))}


def _read_raw(f: Path) -> tuple[dict, dict]:
    data = json.loads(f.read_text(encoding="utf-8"))
    return data.get("meta", {}), data.get("content") or blocktree.EMPTY_DOC


def _read(pid: str) -> tuple[dict, dict]:
    p = _path(pid)
    if not p.exists():
        raise PageError("không có trang này")
    return _read_raw(p)


def _write(pid: str, meta: dict, content: dict) -> None:
    dumped = json.dumps(content, ensure_ascii=False)
    if len(dumped) > MAX_CONTENT:
        raise PageError("nội dung trang quá lớn")
    p = _path(pid)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps({"meta": meta, "content": content}, ensure_ascii=False), encoding="utf-8")
    tmp.replace(p)  # ghi nguyen tu de khong hong file khi mat dien giua chung


def list_pages() -> list[dict]:
    out = []
    for f in _dir().glob("*.json"):
        if ID_RE.match(f.stem):
            out.append(_info(f.stem, _read_raw(f)[0]))
    return sorted(out, key=lambda x: (x["order"], x["created"]))


def get(pid: str) -> dict:
    meta, content = _read(pid)
    return {**_info(pid, meta), "content": content}


def notebook_root(pid: str) -> dict:
    with _lock:
        visited = set()
        while pid not in visited:
            visited.add(pid)
            meta, _ = _read(pid)
            if not meta.get("parent"):
                return _info(pid, meta)
            pid = meta["parent"]
    raise PageError("cây ghi chú có vòng lặp")


def create(title: str = "", parent: str = "", content: dict | None = None, icon: str = "") -> dict:
    with _lock:
        if parent:
            _read(parent)  # trang cha phai ton tai
        pid, now = uuid.uuid4().hex[:10], time.time()
        sibs = [p["order"] for p in list_pages() if p["parent"] == parent]
        meta = {"title": (title or "Chưa đặt tên").strip()[:200], "parent": parent, "icon": _icon(icon),
                "order": (max(sibs) + 1) if sibs else 0, "created": now, "updated": now, "fullWidth": False}
        _write(pid, meta, content if content is not None else blocktree.EMPTY_DOC)
        return get(pid)


def _after_heading(doc: dict, heading: str) -> tuple[list, int]:
    try:
        return blocktree.find_heading_position(doc, heading)
    except ValueError as e:
        raise PageError(str(e)) from e


def create_linked(title: str, parent: str, content: dict | None, *, after_heading: str = "") -> dict:
    """Create the subpage and add a pageLink block without rewriting the existing parent content."""
    with _lock:
        _, doc = _read(parent)
        if after_heading.strip():
            container, idx = _after_heading(doc, after_heading)
        else:
            container, idx = doc.setdefault("content", []), len(doc.get("content", [])) - 1
        child = create(title, parent, content)
        link_block = {"type": "pageLink", "attrs": {"pageId": child["id"], "title": child["title"]}}
        container.insert(idx + 1, link_block)
        try:
            update(parent, content=doc)
        except (OSError, PageError):
            _path(child["id"]).unlink(missing_ok=True)
            raise
        return child


def update(pid: str, title: str | None = None, content: dict | None = None, icon: str | None = None, full_width: bool | None = None) -> dict:
    with _lock:
        meta, doc = _read(pid)
        if title is not None:
            meta["title"] = title.strip()[:200] or "Chưa đặt tên"
        if icon is not None:
            meta["icon"] = _icon(icon)
        if full_width is not None:
            meta["fullWidth"] = bool(full_width)
        meta["updated"] = time.time()
        _write(pid, meta, doc if content is None else content)
        return get(pid)


def append(pid: str, blocks: list[dict]) -> dict:
    with _lock:
        _, doc = _read(pid)
        doc.setdefault("content", []).extend(blocks)
        return update(pid, content=doc)


def _descendants(pid: str, pages: list[dict]) -> list[str]:
    kids = [p["id"] for p in pages if p["parent"] == pid]
    return kids + [d for k in kids for d in _descendants(k, pages)]


def move(pid: str, parent: str, order: float | None = None) -> dict:
    with _lock:
        meta, doc = _read(pid)
        pages = list_pages()
        if parent:
            _read(parent)
            if parent == pid or parent in _descendants(pid, pages):
                raise PageError("không thể chuyển trang vào chính nó hoặc trang con của nó")
        meta["parent"] = parent
        if order is None:
            sibs = [p["order"] for p in pages if p["parent"] == parent and p["id"] != pid]
            order = (max(sibs) + 1) if sibs else 0
        meta["order"] = order
        _write(pid, meta, doc)
        return get(pid)


def delete(pid: str) -> int:
    """Xoa trang va moi trang con; tra ve so trang da xoa."""
    with _lock:
        _read(pid)
        ids = [pid, *_descendants(pid, list_pages())]
        for i in ids:
            _path(i).unlink(missing_ok=True)
        return len(ids)


def search(q: str, limit: int = 20) -> list[dict]:
    terms = [t for t in fold(q).split() if t]
    if not terms:
        return []
    hits = []
    for f in _dir().glob("*.json"):
        if not ID_RE.match(f.stem):
            continue
        meta, doc = _read_raw(f)
        plain = blocktree.plain_text(doc)
        title, text = fold(meta.get("title", "")), fold(plain)
        if all(t in title or t in text for t in terms):
            score = sum(3 for t in terms if t in title) + sum(text.count(t) for t in terms)
            pos = min((text.find(t) for t in terms if t in text), default=0)
            hits.append((score, {**_info(f.stem, meta), "snippet": plain[max(0, pos - 60):pos + 140].replace("\n", " ")}))
    return [h for _, h in sorted(hits, key=lambda x: -x[0])[:limit]]


def export_markdown(pid: str) -> str:
    _, doc = _read(pid)
    return blocktree.to_markdown(doc)


def tree_text(max_items: int = 200) -> str:
    """Cay trang dang chu thut dau dong, cho agent."""
    pages = list_pages()
    by_parent: dict[str, list[dict]] = {}
    for p in pages:
        by_parent.setdefault(p["parent"], []).append(p)
    lines: list[str] = []

    def walk(parent: str, depth: int) -> None:
        for p in by_parent.get(parent, []):
            if len(lines) >= max_items:
                return
            lines.append(f"{'  ' * depth}- {p['icon'] + ' ' if p['icon'] else ''}{p['title']} [{p['id']}]")
            walk(p["id"], depth + 1)

    walk("", 0)
    return "\n".join(lines)


def chat_context(pid: str, *, draft: bool = False) -> str:
    """Doan nhac them vao system prompt khi nguoi dung chat o panel ben phai cua mot trang."""
    try:
        meta, _ = _read(pid)
    except PageError:
        return ""
    if draft:
        return (f'Người dùng đang mở ghi chú "{meta.get("title", "")}" (mã {pid}) và đang ở chế độ xem trước. '
                f'Đọc ghi chú bằng page_read(page_id="{pid}") khi cần ngữ cảnh. '
                'Trả lời hoặc soạn bản nháp ngay trong chat để người dùng xem và tự chèn. '
                'Khi được yêu cầu tách thành trang con, đề xuất tiêu đề và nội dung từng trang trong bản nháp.')
    kids = ", ".join(f"{p['title']} [{p['id']}]" for p in list_pages() if p["parent"] == pid) or "không có"
    return (f'Người dùng đang mở trang "{meta.get("title", "")}" (mã {pid}) trong mục Trang và đang chat ở khung bên phải của trang đó. '
            f"QUY TẮC: mọi yêu cầu viết, soạn, tóm tắt, sửa nội dung đều mặc định phải GHI VÀO TRANG NÀY bằng page_update (mode replace nếu trang đang trống hoặc cần viết lại, mode append để thêm vào cuối), "
            f"kể cả khi người dùng không nói 'trang này'. Nội dung là một danh sách các block có cấu trúc "
            "(ví dụ {\"type\": \"heading\", \"level\": 2, \"text\": \"...\"}, {\"type\": \"paragraph\", \"text\": \"...\"}, "
            "{\"type\": \"bullet_list\", \"items\": [...]}, {\"type\": \"toggle\", \"text\": \"...\", \"children\": [...]}, "
            "{\"type\": \"code\", \"language\": \"...\", \"text\": \"...\"}, {\"type\": \"callout\", \"icon\": \"💡\", \"color\": \"blue\", \"text\": \"...\"}), "
            "không phải markdown hay văn bản thô. "
            f"Khi được yêu cầu tạo hoặc tách thành trang con, gọi page_create với parent_id={pid} và link_in_parent=true. "
            "Nếu người dùng chỉ một mục, đọc trang trước rồi truyền nguyên văn tên tiêu đề đó qua after_heading. "
            "Khi tách theo nhiều mục, đặt liên kết sau tiêu đề tương ứng. Tool sẽ tự chèn liên kết và giữ nội dung đang có. "
            f"KHÔNG tạo file docx/xlsx/pptx/pdf trừ khi người dùng yêu cầu rõ ràng định dạng file đó. Đọc trang bằng page_read trước khi sửa phần đã có. "
            f"Trang con hiện có: {kids}. Dùng page_list để xem cả cây trang. Sau khi ghi xong, trả lời 1-2 câu nói rõ bạn đã viết gì và ở trang nào, không chép lại cả nội dung vào khung chat.")


MAX_IMAGE_BYTES = 10 * 1024 * 1024
ASSET_RE = re.compile(r"^[a-f0-9]{32}\.(?:png|jpg|gif|webp)$")


def _icon(value: str) -> str:
    if value.startswith("/api/pages/assets/") and ASSET_RE.fullmatch(value.rsplit("/", 1)[-1]):
        return value
    return value[:32] if not value.startswith(("/", "http:", "https:")) else ""


def save_image(data: str) -> str:
    """Store raster images locally; never fetch remote URLs or accept active SVG."""
    if len(data) > ((MAX_IMAGE_BYTES + 2) // 3) * 4:
        raise PageError("Ảnh vượt quá 10 MB")
    try:
        raw = base64.b64decode(data, validate=True)
    except (ValueError, binascii.Error) as e:
        raise PageError("Dữ liệu ảnh không hợp lệ") from e
    if not raw or len(raw) > MAX_IMAGE_BYTES:
        raise PageError("Ảnh trống hoặc vượt quá 10 MB")
    if raw.startswith(b"\x89PNG\r\n\x1a\n"):
        ext = "png"
    elif raw.startswith(b"\xff\xd8\xff"):
        ext = "jpg"
    elif raw.startswith((b"GIF87a", b"GIF89a")):
        ext = "gif"
    elif raw.startswith(b"RIFF") and raw[8:12] == b"WEBP":
        ext = "webp"
    else:
        raise PageError("Chỉ hỗ trợ ảnh PNG, JPEG, GIF hoặc WebP")
    name = f"{uuid.uuid4().hex}.{ext}"
    target = _dir() / "assets"
    target.mkdir(exist_ok=True)
    (target / name).write_bytes(raw)
    return f"/api/pages/assets/{name}"


def image_path(name: str) -> Path:
    if not ASSET_RE.fullmatch(name):
        raise PageError("mã ảnh không hợp lệ")
    path = _dir() / "assets" / name
    if not path.is_file():
        raise PageError("không có ảnh này")
    return path
