"""Schema JSON phang, de LLM sinh, cho noi dung trang. Agent gui mot danh sach block don gian
(vi du {"type":"heading","level":2,"text":"..."}); to_prosemirror() chuyen thanh TipTap/ProseMirror doc day du."""
import json

PageErrorMsg = "nội dung phải là một danh sách block JSON hợp lệ"


def _text_node(text: str) -> list[dict]:
    return [{"type": "text", "text": text}] if text else []


def _paragraph(text: str) -> dict:
    return {"type": "paragraph", "content": _text_node(text)}


def _convert_block(b: dict) -> dict:
    t = b.get("type")
    if t == "paragraph":
        return _paragraph(b.get("text", ""))
    if t == "heading":
        level = b.get("level", 1)
        level = level if level in (1, 2, 3) else 1
        return {"type": "heading", "attrs": {"level": level}, "content": _text_node(b.get("text", ""))}
    if t in ("bullet_list", "ordered_list"):
        node_type = "bulletList" if t == "bullet_list" else "orderedList"
        items = [{"type": "listItem", "content": [_paragraph(str(item))]} for item in b.get("items", [])]
        return {"type": node_type, "content": items}
    if t == "task_list":
        items = []
        for item in b.get("items", []):
            text = item.get("text", "") if isinstance(item, dict) else str(item)
            checked = bool(item.get("checked")) if isinstance(item, dict) else False
            items.append({"type": "taskItem", "attrs": {"checked": checked}, "content": [_paragraph(text)]})
        return {"type": "taskList", "content": items}
    if t == "toggle":
        children = [_convert_block(c) for c in b.get("children", [])]
        return {"type": "toggle", "attrs": {"open": bool(b.get("open", False))}, "content": [_paragraph(b.get("text", "")), *children]}
    if t == "code":
        return {"type": "codeBlock", "attrs": {"language": b.get("language") or None}, "content": _text_node(b.get("text", ""))}
    if t == "callout":
        return {"type": "callout", "attrs": {"icon": b.get("icon", "💡"), "color": b.get("color", "gray")}, "content": [_paragraph(b.get("text", ""))]}
    if t == "quote":
        return {"type": "blockquote", "content": [_paragraph(b.get("text", ""))]}
    if t == "divider":
        return {"type": "horizontalRule"}
    if t == "table":
        rows = b.get("rows", [])
        table_rows = []
        for ri, row in enumerate(rows):
            cell_type = "tableHeader" if ri == 0 else "tableCell"
            cells = [{"type": cell_type, "content": [_paragraph(str(v))]} for v in row]
            table_rows.append({"type": "tableRow", "content": cells})
        return {"type": "table", "content": table_rows}
    # fallback: treat unknown type as plain paragraph using available text
    return _paragraph(b.get("text", "") or json.dumps(b, ensure_ascii=False))


def to_prosemirror(blocks: list[dict]) -> list[dict]:
    if not isinstance(blocks, list):
        raise ValueError(PageErrorMsg)
    return [_convert_block(b) for b in blocks if isinstance(b, dict)]


def parse_blocks(raw: str) -> list[dict]:
    """Agent gui noi dung dang chuoi JSON (danh sach block); parse va bao loi ro rang neu sai dinh dang."""
    if not raw or not raw.strip():
        return []
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(PageErrorMsg) from e
    if not isinstance(data, list):
        raise ValueError(PageErrorMsg)
    return data
