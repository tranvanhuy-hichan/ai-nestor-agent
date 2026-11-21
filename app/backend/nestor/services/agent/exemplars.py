"""Dynamic Few-Shot Exemplars Injection: Tiêm động ví dụ mẫu theo ngữ cảnh (Hermes Agent).

Thay vì nhồi nhét hàng nghìn dòng ví dụ tĩnh vào System Prompt gây tốn token và loãng ngữ cảnh,
hệ thống tự động phát hiện ý định (Intent) của người dùng trong tin nhắn hiện tại và chỉ nạp
1-2 ví dụ mẫu chuẩn mực, súc tích nhất cho lượt xử lý đó.
"""
from __future__ import annotations

import re

EXEMPLARS: dict[str, dict] = {
    "coding": {
        "keywords": ["code", "lập trình", "viết hàm", "debug", "sửa lỗi", "refactor", "test", "python", "javascript", "typescript", "tạo file"],
        "title": "Mẫu giải quyết bài toán Lập trình & Sửa mã nguồn",
        "content": (
            "1. Khám phá trước: Dùng grep hoặc find để định vị file nguồn, dùng read để đọc đúng phạm vi cần sửa.\n"
            "2. Sửa nhỏ & chính xác: Dùng edit thay vì ghi đè cả file. Giữ nguyên định dạng và logic xung quanh.\n"
            "3. Kiểm chứng ngay: Tự chạy lệnh test hoặc syntax check bằng exec để chắc chắn code không lỗi trước khi báo xong."
        )
    },
    "office_nd30": {
        "keywords": ["tờ trình", "công văn", "nghị định 30", "văn bản", "thể thức", "quyết định", "biên bản", "báo cáo"],
        "title": "Mẫu soạn thảo Văn bản Hành chính (Nghị định 30/2020/NĐ-CP)",
        "content": (
            "1. Xác định đúng loại: Dùng `vanban_types` để lấy cấu trúc chuẩn của loại văn bản.\n"
            "2. Soạn đủ các phần: Quốc hiệu, Tiêu ngữ, Tên cơ quan ban hành, Số/ký hiệu, Trích yếu nội dung, Phần căn cứ pháp lý, Các điều khoản/nội dung chi tiết, Nơi nhận và Quyền hạn/Chức vụ người ký.\n"
            "3. Tự rà soát: Dùng `review_vn_document` kiểm tra thể thức và sửa triệt để các cảnh báo trước khi xuất file."
        )
    },
    "excel_data": {
        "keywords": ["excel", "xlsx", "bảng tính", "công thức", "tính toán", "tổng hợp", "công nợ", "doanh thu"],
        "title": "Mẫu xuất Dữ liệu & Bảng tính Excel",
        "content": (
            "1. Định dạng công thức: Luôn dùng công thức chuẩn tiếng Anh (ví dụ `=SUM(B2:B10)`, `=AVERAGE(...)`), không điền số chết vào ô tổng cộng.\n"
            "2. Phân tách rõ ràng: Hàng tiêu đề in đậm, cột số liệu căn phải, cột chữ căn trái, có dòng tổng kết rõ ràng."
        )
    },
    "system_troubleshoot": {
        "keywords": ["tiến trình", "port", "cổng", "ram", "cpu", "hệ thống", "terminal", "service", "chạy ngầm", "kiểm tra máy"],
        "title": "Mẫu kiểm tra & Xử lý sự cố Hệ thống",
        "content": (
            "1. Tự động kiểm tra: TUYỆT ĐỐI không bảo người dùng mở terminal tự chạy lệnh. Hãy TỰ DÙNG `exec` chạy các lệnh `ps`, `top -b -n 1`, `ss -tulpn`, `df -h`.\n"
            "2. Phân tích kết quả: Đọc output trả về từ lệnh, tóm tắt rõ ràng các thông số % CPU, % Memory hoặc tiến trình đang chiếm dụng."
        )
    }
}


def get_dynamic_exemplars(query: str, max_exemplars: int = 2) -> str:
    """Quét ý định câu hỏi và trả về khối ví dụ mẫu chuẩn hóa nếu phù hợp."""
    if not query:
        return ""

    low_query = query.lower()
    selected: list[dict] = []

    for key, data in EXEMPLARS.items():
        if any(kw in low_query for kw in data["keywords"]):
            selected.append(data)
            if len(selected) >= max_exemplars:
                break

    if not selected:
        return ""

    blocks: list[str] = ["## HƯỚNG DẪN MẪU THEO NGỮ CẢNH (Hermes Exemplars):"]
    for ex in selected:
        blocks.append(f"### {ex['title']}:\n{ex['content']}")

    return "\n\n".join(blocks)
