"""Post-Action Verification & Sanity Check: Kiểm chứng tự động sau hành động theo chuẩn Hermes Agent.

Trước khi hoàn tất câu trả lời cho người dùng, Agent tự động kiểm tra lại các sản phẩm/tệp vừa tạo/sửa:
- File có bị rỗng (0 bytes) không.
- Code Python/JSON có bị lỗi cú pháp không.
- Tài liệu Word/Excel/PDF có kích thước hợp lệ không.
- Có sót các placeholder chưa điền (TODO, [Điền vào đây]...) không.
Nếu phát hiện lỗi, hệ thống tự động cảnh báo để Agent sửa lại ngay trước khi bàn giao cho người dùng.
"""
from __future__ import annotations

import ast
import json
from pathlib import Path

FILE_MUTATING_TOOLS = {
    "write", "edit", "patch", "create_cv", "vanban_write_docx",
    "docx_write", "xlsx_write", "save_file", "write_file",
}

PLACEHOLDER_MARKERS = [
    "{{TODO}}", "[Điền vào đây]", "[Chèn nội dung tại đây]",
    "[TODO]", "INSERT_HERE", "TODO: REPLACE",
]


def is_mutating_tool(tool_name: str) -> bool:
    """Kiểm tra xem công cụ có làm thay đổi/tạo mới file không."""
    return tool_name in FILE_MUTATING_TOOLS or "write" in tool_name or "edit" in tool_name or "create" in tool_name


def verify_file(file_path: Path) -> list[str]:
    """Kiểm chứng một tệp vừa được tạo hoặc chỉnh sửa."""
    issues: list[str] = []
    if not file_path.exists():
        return [f"Tệp `{file_path.name}` không tồn tại sau khi công cụ báo thành công."]

    if not file_path.is_file():
        return []

    size = file_path.stat().st_size
    if size == 0:
        return [f"Tệp `{file_path.name}` bị rỗng hoàn toàn (0 bytes)."]

    suffix = file_path.suffix.lower()

    # 1. Kiểm tra tài liệu nhị phân (Word, Excel, PowerPoint, PDF)
    if suffix in (".docx", ".xlsx", ".pptx", ".pdf"):
        if size < 500:
            issues.append(f"Tệp tài liệu `{file_path.name}` có dung lượng bất thường ({size} bytes), có thể bị lỗi khi xuất.")
        return issues

    # 2. Kiểm tra tệp văn bản / mã nguồn
    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return [f"Không đọc được nội dung tệp `{file_path.name}`: {e}"]

    # Kiểm tra placeholder chưa điền
    found_placeholders = [p for p in PLACEHOLDER_MARKERS if p in content]
    if found_placeholders:
        issues.append(f"Tệp `{file_path.name}` còn sót ký hiệu mẫu chưa điền: {', '.join(found_placeholders[:3])}.")

    # Kiểm tra cú pháp JSON
    if suffix == ".json":
        try:
            json.loads(content)
        except Exception as je:
            issues.append(f"Tệp JSON `{file_path.name}` bị lỗi cú pháp: {je}")

    # Kiểm tra cú pháp Python
    elif suffix == ".py":
        try:
            ast.parse(content, filename=file_path.name)
        except SyntaxError as se:
            issues.append(f"Tệp Python `{file_path.name}` bị lỗi cú pháp tại dòng {se.lineno}: {se.msg}")

    return issues


def verify_turn_outputs(workdir: Path, modified_paths: set[str]) -> list[str]:
    """Kiểm tra toàn bộ danh sách tệp đã thay đổi trong lượt."""
    all_issues: list[str] = []
    for rel_or_abs in modified_paths:
        p = Path(rel_or_abs)
        target = p if p.is_absolute() else (workdir / p)
        issues = verify_file(target)
        all_issues.extend(issues)
    return all_issues
