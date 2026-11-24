"""Tool kb_search: tìm trong kho tài liệu người dùng đã thêm và trả đoạn kèm nguồn để agent trích dẫn."""
from nestor.services import knowledge
from . import tool


def source_tag(hit: dict) -> str:
    loc = hit["loc"].replace("]", "］").replace("\n", " ").replace("\r", " ")
    if hit.get("chunk_id") is not None:
        loc = f"{loc}#chunk={hit['chunk_id']}"
    name = hit["name"].translate(str.maketrans({"|": "｜", "]": "］", "\n": " ", "\r": " "}))
    return f"[[src:{hit['doc_id']}|{name}|{loc}]]"


def format_hits(hits: list[dict]) -> str:
    out = []
    for i, h in enumerate(hits, start=1):
        text = " ".join(h["text"].split())
        out.append(f"[{i}] thẻ nguồn: {source_tag(h)}\n{text[:900]}")
    return "\n\n".join(out)


@tool("kb_search", "Tìm trong kho tài liệu của người dùng (PDF, Word, Excel, PowerPoint, văn bản đã thêm ở mục Tài liệu). Chỉ dùng khi người dùng hỏi về nội dung tài liệu của họ, không dùng cho kiến thức chung, ngày giờ, tin tức, sự kiện. "
      "Mỗi đoạn trả về kèm một thẻ nguồn dạng [[src:...]]; khi trả lời chèn nguyên văn thẻ đó ở cuối ý tương ứng.",
      {"query": ("string", "câu hỏi hoặc từ khóa cần tìm trong tài liệu"), "limit": ("integer", "số đoạn tối đa (mặc định 6)")}, required=["query"])
def kb_search(ctx, query, limit=6):
    return format_hits(knowledge.search(query, int(limit), ctx.kb_category_id)) or "không tìm thấy đoạn nào liên quan trong kho tài liệu"
