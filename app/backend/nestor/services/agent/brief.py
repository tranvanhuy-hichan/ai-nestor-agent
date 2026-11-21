"""Mau automation dung san: 'Tom tat buoi sang 7:30'."""
import re

from nestor.services import scheduler

NAME = "Tóm tắt buổi sáng"
PROMPT = """Hãy lập BẢN TÓM TẮT BUỔI SÁNG cho tôi, tiếng Việt, ngắn gọn dạng gạch đầu dòng, chia mục:
1. Email mới: dùng các tool email/MCP đã kết nối (Outlook/Gmail) để tóm tắt email chưa đọc từ hôm qua, đánh dấu cái cần trả lời gấp và người gửi. Nếu chưa kết nối email thì ghi một dòng 'Chưa kết nối email'.
2. Lịch hôm nay: dùng tool lịch (Google Calendar/Outlook) liệt kê cuộc họp, giờ, địa điểm, chuẩn bị gì. Nếu chưa kết nối thì ghi 'Chưa kết nối lịch'.
3. Việc nền và việc quá hạn: dùng task_status để liệt kê việc chạy nền gần đây (đang chạy, lỗi); đọc HEARTBEAT.md và các ghi nhớ nếu có hạn cần nhắc.
4. Gợi ý 3 việc nên làm đầu tiên trong ngày.
Không gửi email, không đổi lịch, không làm gì ngoài việc đọc và tóm tắt."""


def _cron(hhmm: str) -> str:
    m = re.fullmatch(r"([01]?\d|2[0-3]):([0-5]\d)", (hhmm or "").strip())
    if not m:
        raise scheduler.ScheduleError("giờ phải có dạng HH:MM, ví dụ 07:30")
    return f"{int(m.group(2))} {int(m.group(1))} * * *"


def create(hhmm: str = "07:30", provider: str | None = None) -> dict:
    """Tao (hoac cap nhat neu da co) automation tom tat moi sang. notify=True: ket qua vao Hop thu va duoc day sang Telegram/Zalo da bat."""
    job = {"name": NAME, "schedule": _cron(hhmm), "prompt": PROMPT, "provider": provider, "enabled": True, "notify": True}
    existing = next((j for j in scheduler.list_jobs() if j["name"] == NAME), None)
    return {"id": scheduler.save_job(job, existing["id"] if existing else None), "name": NAME, "schedule": job["schedule"], "updated": bool(existing)}
