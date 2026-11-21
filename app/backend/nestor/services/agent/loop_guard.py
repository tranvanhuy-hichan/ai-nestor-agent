"""Bộ phát hiện kẹt vòng lặp (Loop Guard & Stuck Detector) theo chuẩn Hermes Agent.

Phát hiện khi Agent gọi lặp đi lặp lại cùng một công cụ với đối số giống nhau
hoặc rơi vào chu kỳ luẩn quẩn (ping-pong cycles) mà không tạo ra tiến triển mới.
Khi phát hiện, LoopGuard sẽ can thiệp ngay lập tức:
1. Phát cảnh báo `notice` lên UI cho người dùng biết.
2. Tiêm một hướng dẫn hệ thống trực tiếp vào lượt tiếp theo để ép Agent thay đổi chiến thuật.
"""
from __future__ import annotations

import json
from typing import Any


class LoopGuard:
    def __init__(self, max_consecutive_duplicates: int = 3, cycle_threshold: int = 2):
        self.max_consecutive_duplicates = max_consecutive_duplicates
        self.cycle_threshold = cycle_threshold
        # Lưu các lượt gọi công cụ dạng (tool_name, sorted_json_args)
        self.call_history: list[tuple[str, str]] = []

    def _normalize(self, name: str, args: Any) -> tuple[str, str]:
        try:
            if isinstance(args, str):
                parsed = json.loads(args)
            elif isinstance(args, dict):
                parsed = args
            else:
                parsed = str(args)
            serialized = json.dumps(parsed, sort_keys=True, ensure_ascii=False)
        except Exception:
            serialized = str(args)
        return (name, serialized)

    def record_and_check(self, tool_calls: list[dict]) -> tuple[bool, str, str]:
        """Ghi nhận các tool call mới và kiểm tra xem có rơi vào trạng thái kẹt không.

        Returns:
            (is_stuck, system_warning_message, ui_notice)
        """
        if not tool_calls:
            return False, "", ""

        new_calls = [self._normalize(c.get("name", ""), c.get("args", {})) for c in tool_calls]
        self.call_history.extend(new_calls)

        # 1. Kiểm tra lặp liên tiếp một công cụ với cùng đối số
        if len(self.call_history) >= self.max_consecutive_duplicates:
            last_n = self.call_history[-self.max_consecutive_duplicates:]
            if all(call == last_n[0] for call in last_n):
                tool_name, args_str = last_n[0]
                args_preview = args_str[:120] + ("..." if len(args_str) > 120 else "")
                warn_msg = (
                    f"[system] PHÁT HIỆN KẸT VÒNG LẶP (LOOP GUARD): Bạn vừa gọi công cụ '{tool_name}' "
                    f"{self.max_consecutive_duplicates} lần liên tiếp với cùng tham số `{args_preview}` mà không tạo ra tiến triển mới. "
                    "DỪNG NGAY CHIẾN THUẬT NÀY. Hãy phân tích kỹ lý do lỗi, chuyển sang phương án tiếp cận khác "
                    "(ví dụ: đổi lệnh, đọc file khác, tìm kiếm tài liệu khác) hoặc trả lời người dùng nếu thấy thiếu thông tin."
                )
                ui_notice = f"LoopGuard: Phát hiện lặp công cụ '{tool_name}', đang can thiệp đổi phương án..."
                return True, warn_msg, ui_notice

        # 2. Kiểm tra chu kỳ lặp luân phiên (Cycle / Ping-Pong: A -> B -> A -> B)
        # Kiểm tra chu kỳ độ dài 2 (4 cuộc gọi: A, B, A, B)
        if len(self.call_history) >= 4:
            c1, c2, c3, c4 = self.call_history[-4:]
            if c1 == c3 and c2 == c4 and c1 != c2:
                t1, t2 = c1[0], c2[0]
                warn_msg = (
                    f"[system] PHÁT HIỆN CHU KỲ LẶP (PING-PONG LOOP): Bạn đang luân phiên gọi qua lại giữa '{t1}' và '{t2}' "
                    "với cùng dữ liệu mà không có kết quả mới. Hãy dừng chu kỳ này ngay và chọn hướng giải quyết khác."
                )
                ui_notice = f"LoopGuard: Phát hiện vòng lặp luân phiên giữa '{t1}' và '{t2}'."
                return True, warn_msg, ui_notice

        # Kiểm tra chu kỳ độ dài 3 (6 cuộc gọi: A, B, C, A, B, C)
        if len(self.call_history) >= 6:
            c1, c2, c3, c4, c5, c6 = self.call_history[-6:]
            if c1 == c4 and c2 == c5 and c3 == c6 and len({c1, c2, c3}) == 3:
                tools_in_cycle = ", ".join(c[0] for c in (c1, c2, c3))
                warn_msg = (
                    f"[system] PHÁT HIỆN CHU KỲ LẶP 3 BƯỚC: Chuỗi gọi ({tools_in_cycle}) đang lặp lại. "
                    "Dừng ngay việc lặp chuỗi này và chuyển hướng thực thi."
                )
                ui_notice = f"LoopGuard: Phát hiện chu kỳ lặp 3 công cụ ({tools_in_cycle})."
                return True, warn_msg, ui_notice

        return False, "", ""

    def reset(self) -> None:
        """Xóa lịch sử khi bắt đầu phiên hoặc câu hỏi mới."""
        self.call_history.clear()
