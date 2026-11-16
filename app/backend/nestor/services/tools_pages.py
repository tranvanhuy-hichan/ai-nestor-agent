"""Tool de agent doc/ghi 'Trang' (kieu Notion) trong workspace/pages."""
from . import pages
from .tools import tool


def _fmt(p: dict) -> str:
    return f"{p['title']} [{p['id']}]"


@tool("page_list", "Liệt kê cây trang (Trang kiểu Notion của người dùng), mỗi dòng có mã trang trong [ ].", {}, risk="safe")
def page_list(ctx):
    return pages.tree_text() or "Chưa có trang nào."


@tool("page_search", "Tìm trang theo từ khóa trong tiêu đề và nội dung (không phân biệt dấu).", {"query": ("string", "từ khóa")}, risk="safe")
def page_search(ctx, query):
    hits = pages.search(query)
    return "\n".join(f"- {_fmt(h)}: …{h['snippet']}…" for h in hits) or "Không thấy trang nào khớp."


@tool("page_read", "Đọc nội dung một trang (markdown) theo mã trang.", {"page_id": ("string", "mã trang trong [ ]")}, risk="safe")
def page_read(ctx, page_id):
    p = pages.get(page_id)
    return f"# {p['title']}\n(mã {p['id']}, trang cha: {p['parent'] or 'gốc'})\n\n{p['content']}"


@tool("page_create", "Tạo trang mới (nội dung markdown). parent_id để trống = trang gốc. Trả về mã trang.",
      {"title": ("string", "tiêu đề"), "content": ("string", "nội dung markdown"), "parent_id": ("string", "mã trang cha, để trống nếu là trang gốc")},
      required=["title"], risk="file")
def page_create(ctx, title, content="", parent_id=""):
    p = pages.create(title, parent_id, content)
    return f"Đã tạo trang {_fmt(p)}."


@tool("page_update", "Sửa trang: mode 'append' thêm vào cuối, 'replace' thay toàn bộ nội dung. Có thể đổi tiêu đề.",
      {"page_id": ("string", "mã trang"), "content": ("string", "nội dung markdown"), "mode": ("string", "append (mặc định) hoặc replace"), "title": ("string", "tiêu đề mới, tùy chọn")},
      required=["page_id"], risk="file")
def page_update(ctx, page_id, content="", mode="append", title=None):
    if mode not in ("append", "replace"):
        raise ValueError("mode phải là append hoặc replace")
    if title:
        pages.update(page_id, title=title)
    if content:
        p = pages.append(page_id, content) if mode == "append" else pages.update(page_id, content=content)
    else:
        p = pages.get(page_id)
    return f"Đã cập nhật trang {_fmt(p)}."
