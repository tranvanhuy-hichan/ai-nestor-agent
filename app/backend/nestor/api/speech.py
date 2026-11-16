"""Generate real audio independently of installed browser/system voices."""
import io
import threading
from typing import Literal

from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel, Field
from gtts import gTTS

AUTO = True
router = APIRouter()
_slots = threading.BoundedSemaphore(2)


class SpeechBody(BaseModel):
    text: str = Field(min_length=1, max_length=600)
    lang: Literal["vi", "en", "ja", "ko", "zh-CN", "fr", "de", "es"] = "vi"


@router.post("/speech")
def speech(body: SpeechBody):
    text = body.text.strip()
    if not text:
        raise HTTPException(422, "Nội dung đọc không được để trống")
    if not _slots.acquire(blocking=False):
        raise HTTPException(429, "Giọng đọc đang bận. Vui lòng thử lại.")
    try:
        # Fixed service/languages; no caller-controlled URL or voice commands.
        # Audio stays in memory and is never stored alongside user documents.
        out = io.BytesIO()
        for chunk in gTTS(text, lang=body.lang, lang_check=False, timeout=(5, 10)).stream():
            out.write(chunk)
            if out.tell() > 2_000_000:
                raise ValueError("Audio exceeds size limit")
        if not out.tell():
            raise ValueError("Empty audio")
        return Response(out.getvalue(), media_type="audio/mpeg", headers={"Cache-Control": "no-store"})
    except Exception:
        # Upstream exception text may contain submitted content; do not expose it.
        raise HTTPException(503, "Không tạo được giọng đọc. Vui lòng kiểm tra kết nối mạng và thử lại.") from None
    finally:
        _slots.release()
