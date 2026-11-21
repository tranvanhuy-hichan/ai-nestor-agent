"""Thuật toán cắt tỉa thông minh (Head-Tail Truncation with Middle Elision).

Học hỏi từ Trajectory Compressor và Output Truncation của Hermes Agent:
Bảo vệ phần đầu (head) và phần đuôi (tail) của output/nội dung file,
lược bỏ phần giữa khi vượt quá giới hạn ký tự.
Điều này giúp mô hình AI giữ được:
1. Phần đầu: Lệnh khởi động, import, khai báo lớp, header của dữ liệu.
2. Phần đuôi: Trạng thái kết thúc, exit code, thông báo lỗi (traceback), tóm tắt kết quả.
"""
from __future__ import annotations


def truncate_middle(text: str, max_chars: int = 12000, head_ratio: float = 0.4, marker: str | None = None) -> str:
    """Cắt tỉa văn bản dài bằng cách giữ lại phần đầu và phần đuôi, ẩn phần ở giữa.
    
    Args:
        text: Văn bản đầu vào cần cắt tỉa.
        max_chars: Số ký tự tối đa cho phép.
        head_ratio: Tỷ lệ ký tự dành cho phần đầu (0.0 đến 1.0, mặc định 0.4 = 40% đầu, 60% đuôi).
        marker: Chuỗi thông báo thay thế phần bị ẩn (nếu None sẽ tự sinh).
        
    Returns:
        Chuỗi đã được cắt tỉa nếu vượt max_chars, hoặc nguyên bản nếu <= max_chars.
    """
    if not text or len(text) <= max_chars:
        return text

    head_chars = max(100, int(max_chars * head_ratio))
    tail_chars = max(100, max_chars - head_chars)

    # Cố gắng cắt theo ngắt dòng gần nhất để tránh gãy dòng code/log
    head_part = text[:head_chars]
    last_newline_head = head_part.rfind("\n")
    if last_newline_head > head_chars // 2:
        head_part = head_part[:last_newline_head]

    tail_part = text[-tail_chars:]
    first_newline_tail = tail_part.find("\n")
    if 0 < first_newline_tail < tail_chars // 2:
        tail_part = tail_part[first_newline_tail + 1:]

    omitted_chars = len(text) - len(head_part) - len(tail_part)
    omitted_text = text[len(head_part):len(text) - len(tail_part)]
    omitted_lines = omitted_text.count("\n")

    if marker is None:
        lines_info = f" ({omitted_lines} dòng)" if omitted_lines > 1 else ""
        marker = f"\n\n[... Đã ẩn {omitted_chars:,} ký tự{lines_info} ở giữa để tối ưu ngữ cảnh. Gọi lại công cụ với bộ lọc cụ thể hơn nếu cần xem phần này ...]\n\n"

    return f"{head_part}{marker}{tail_part}"
