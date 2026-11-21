"""Tool de agent doc/ghi 'Trang' (kieu Notion) trong workspace/pages."""
from nestor.services import pages
from . import block_dsl, tool


def _fmt(p: dict) -> str:
    return f"{p['title']} [{p['id']}]"


def _content_doc(raw: str) -> dict | None:
    blocks = block_dsl.parse_blocks(raw)
    if not blocks:
        return None
    return {"type": "doc", "content": block_dsl.to_prosemirror(blocks)}


@tool("page_list", "Liệt kê cây trang (Trang kiểu Notion của người dùng), mỗi dòng có mã trang trong [ ].", {}, risk="safe")
def page_list(ctx):
    return pages.tree_text() or "Chưa có trang nào."


@tool("page_search", "Tìm trang theo từ khóa trong tiêu đề và nội dung (không phân biệt dấu).", {"query": ("string", "từ khóa")}, risk="safe")
def page_search(ctx, query):
    hits = pages.search(query)
    return "\n".join(f"- {_fmt(h)}: …{h['snippet']}…" for h in hits) or "Không thấy trang nào khớp."


@tool("page_read", "Đọc nội dung một trang theo mã trang (dạng văn bản rút gọn, chỉ để đọc).", {"page_id": ("string", "mã trang trong [ ]")}, risk="safe")
def page_read(ctx, page_id):
    from nestor.services.office import blocktree

    p = pages.get(page_id)
    text = blocktree.plain_text(p["content"])
    return f"# {p['title']}\n(mã {p['id']}, trang cha: {p['parent'] or 'gốc'})\n\n{text}"


_CONTENT_DESC = ('danh sách block dạng chuỗi JSON, ví dụ: [{"type":"heading","level":2,"text":"..."},{"type":"paragraph","text":"..."},'
                 '{"type":"bullet_list","items":["...","..."]},{"type":"task_list","items":[{"text":"...","checked":false}]},'
                 '{"type":"toggle","text":"...","open":false,"children":[...]},{"type":"code","language":"python","text":"..."},'
                 '{"type":"callout","icon":"💡","color":"blue","text":"..."},{"type":"quote","text":"..."},{"type":"divider"},'
                 '{"type":"table","rows":[["h1","h2"],["a","b"]]}]')


@tool("page_create", "Tạo trang mới. Khi tạo trang con, có thể chèn liên kết vào trang cha trong cùng thao tác.",
      {"title": ("string", "tiêu đề"), "content": ("string", _CONTENT_DESC), "parent_id": ("string", "mã trang cha, để trống nếu là trang gốc"),
       "link_in_parent": ("boolean", "chèn liên kết vào trang cha"), "after_heading": ("string", "tiêu đề trong trang cha để chèn ngay sau đó, bỏ trống để chèn cuối trang")},
      required=["title"], risk="file")
def page_create(ctx, title, content="", parent_id="", link_in_parent=False, after_heading=""):
    linked = link_in_parent or bool(after_heading.strip())
    if linked and not parent_id:
        raise pages.PageError("cần mã trang cha để chèn liên kết")
    if ctx.confirm_writes and not ctx.full_access:
        detail = f"Tạo trang {title}" + (f" và chèn liên kết vào trang {parent_id}" if linked else "")
        if not ctx.approve("file_write", detail):
            raise pages.PageError("không được phép tạo trang")
    doc = _content_doc(content)
    p = pages.create_linked(title, parent_id, doc, after_heading=after_heading) if linked else pages.create(title, parent_id, doc)
    return f"Đã tạo trang {_fmt(p)}." + (f" Đã chèn liên kết vào trang cha [{parent_id}]." if linked else "")


@tool("page_update", "Sửa trang: mode 'append' thêm vào cuối, 'replace' thay toàn bộ nội dung. Có thể đổi tiêu đề.",
      {"page_id": ("string", "mã trang"), "content": ("string", _CONTENT_DESC), "mode": ("string", "append (mặc định) hoặc replace"), "title": ("string", "tiêu đề mới, tùy chọn")},
      required=["page_id"], risk="file")
def page_update(ctx, page_id, content="", mode="append", title=None):
    if mode not in ("append", "replace"):
        raise ValueError("mode phải là append hoặc replace")
    if (title or content) and ctx.confirm_writes and not ctx.full_access and not ctx.approve("file_write", f"Sửa trang {page_id} ({mode})"):
        raise pages.PageError("không được phép sửa trang")
    if title:
        pages.update(page_id, title=title)
    if content:
        blocks = block_dsl.to_prosemirror(block_dsl.parse_blocks(content))
        p = pages.append(page_id, blocks) if mode == "append" else pages.update(page_id, content={"type": "doc", "content": blocks})
    else:
        p = pages.get(page_id)
    return f"Đã cập nhật trang {_fmt(p)}."
