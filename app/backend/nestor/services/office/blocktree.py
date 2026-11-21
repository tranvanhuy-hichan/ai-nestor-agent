"""Cac ham duyet cay TipTap/ProseMirror JSON doc dung chung cho pages.py:
tim vi tri sau mot tieu de, lay plain text de tim kiem, va xuat markdown."""
from typing import Any

from nestor.core.text import fold

EMPTY_DOC: dict = {"type": "doc", "content": [{"type": "paragraph"}]}


def _text_of(node: dict) -> str:
    if node.get("type") == "text":
        return node.get("text", "")
    return "".join(_text_of(c) for c in node.get("content", []))


def find_heading_position(doc: dict, heading: str) -> tuple[list, int]:
    """Tim block heading co text khop chinh xac (bo dau) trong toan bo cay, ke ca long trong toggle/callout.
    Bat buoc dung 1 ket qua khop; tra ve (danh sach cha, chi so) de chen sibling ngay sau heading do."""
    wanted = fold(heading.strip())
    matches: list[tuple[list, int]] = []

    def walk(container: list) -> None:
        for i, node in enumerate(container):
            if node.get("type") == "heading" and fold(_text_of(node).strip()) == wanted:
                matches.append((container, i))
            if node.get("content"):
                walk(node["content"])

    walk(doc.get("content", []))
    if len(matches) != 1:
        raise ValueError("cần một tiêu đề duy nhất khớp chính xác trong trang cha")
    return matches[0]


def plain_text(doc: dict) -> str:
    """Noi toan bo text trong doc, chen xuong dong giua cac block cap cao de lam snippet tim kiem."""
    lines: list[str] = []

    def walk(container: list) -> None:
        for node in container:
            t = node.get("type")
            if t == "text":
                if lines:
                    lines[-1] += node.get("text", "")
                else:
                    lines.append(node.get("text", ""))
                continue
            text = _text_of(node) if not node.get("content") else ""
            if text:
                lines.append(text)
            if node.get("content"):
                walk(node["content"])
            if t not in (None, "text"):
                lines.append("")

    walk(doc.get("content", []))
    return "\n".join(line for line in lines if line.strip())


_COLOR_LABEL = {"gray": "Ghi chú", "blue": "Lưu ý", "green": "Mẹo", "yellow": "Cảnh báo", "red": "Quan trọng", "purple": "Ý tưởng"}


def to_markdown(doc: dict) -> str:
    """Xuat mot ban markdown doc-duoc tu TipTap doc JSON, chi dung cho tinh nang Export."""
    out: list[str] = []

    def inline(nodes: list) -> str:
        parts = []
        for n in nodes or []:
            if n.get("type") != "text":
                parts.append(_text_of(n))
                continue
            text = n.get("text", "")
            for m in n.get("marks", []):
                if m.get("type") == "bold":
                    text = f"**{text}**"
                elif m.get("type") == "italic":
                    text = f"*{text}*"
                elif m.get("type") == "code":
                    text = f"`{text}`"
            parts.append(text)
        return "".join(parts)

    def list_items(items: list, ordered: bool, depth: int = 0) -> None:
        for i, item in enumerate(items):
            prefix = "  " * depth + (f"{i + 1}. " if ordered else "- ")
            texts = [inline(c.get("content", [])) for c in item.get("content", []) if c.get("type") == "paragraph"]
            out.append(prefix + " ".join(t for t in texts if t))
            for c in item.get("content", []):
                if c.get("type") == "bulletList":
                    list_items(c.get("content", []), False, depth + 1)
                elif c.get("type") == "orderedList":
                    list_items(c.get("content", []), True, depth + 1)

    def block(node: dict) -> None:
        t = node.get("type")
        if t == "paragraph":
            out.append(inline(node.get("content", [])))
        elif t == "heading":
            level = node.get("attrs", {}).get("level", 1)
            out.append("#" * level + " " + inline(node.get("content", [])))
        elif t == "bulletList":
            list_items(node.get("content", []), False)
        elif t == "orderedList":
            list_items(node.get("content", []), True)
        elif t == "taskList":
            for item in node.get("content", []):
                checked = "x" if item.get("attrs", {}).get("checked") else " "
                texts = [inline(c.get("content", [])) for c in item.get("content", []) if c.get("type") == "paragraph"]
                out.append(f"- [{checked}] " + " ".join(t2 for t2 in texts if t2))
        elif t == "toggle":
            kids = node.get("content", [])
            out.append(f"<details>\n<summary>{_text_of(kids[0]) if kids else ''}</summary>\n")
            for child in kids[1:]:
                block(child)
            out.append("</details>")
        elif t == "codeBlock":
            lang = node.get("attrs", {}).get("language") or ""
            out.append(f"```{lang}\n{_text_of(node)}\n```")
        elif t == "callout":
            icon = node.get("attrs", {}).get("icon", "")
            color = node.get("attrs", {}).get("color", "gray")
            label = _COLOR_LABEL.get(color, "Ghi chú")
            text = inline(node.get("content", [])) if node.get("content") else _text_of(node)
            out.append(f"> {icon} **{label}**: {text}")
        elif t == "blockquote":
            out.append("> " + _text_of(node))
        elif t == "horizontalRule":
            out.append("---")
        elif t == "table":
            rows = node.get("content", [])
            for ri, row in enumerate(rows):
                cells = [inline(c.get("content", [{}])[0].get("content", []) if c.get("content") else []) for c in row.get("content", [])]
                out.append("| " + " | ".join(cells) + " |")
                if ri == 0:
                    out.append("| " + " | ".join("---" for _ in cells) + " |")
        elif t == "pageLink":
            attrs = node.get("attrs", {})
            out.append(f"[{attrs.get('title', '')}](/pages/{attrs.get('pageId', '')})")
        elif t == "image":
            attrs = node.get("attrs", {})
            out.append(f"![{attrs.get('alt', '')}]({attrs.get('src', '')})")
        else:
            text = _text_of(node)
            if text:
                out.append(text)
        out.append("")

    for node in doc.get("content", []):
        block(node)
    return "\n".join(out).strip() + "\n"
