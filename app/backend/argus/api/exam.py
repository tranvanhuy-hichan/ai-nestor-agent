"""Xáo đề thi: giáo viên tải đề .docx lên, nhận lại nhiều mã đề + bảng đáp án (+ .zip)."""
import re
import shutil
import uuid
import zipfile
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from ..core import config as cfgmod
from ..services import exam_shuffle

AUTO = True
router = APIRouter()
MAX_BYTES = 25 * 1024 * 1024
_ID = re.compile(r"[a-f0-9]{12}")


def _root() -> Path:
    return cfgmod.load().workspace_path() / "exams"


def _entry(eid: str, p: Path) -> dict:
    return {"name": p.name, "size": p.stat().st_size, "url": f"/api/exam/{eid}/file/{p.name}"}


@router.post("/exam/shuffle")
async def shuffle(file: UploadFile = File(...), versions: int = Form(4), start_code: int = Form(101), keep_order: bool = Form(False),
                  strip_marks: bool = Form(True), answers: str = Form("")):
    name = Path(file.filename or "de-thi.docx").name
    if not name.lower().endswith(".docx"):
        raise HTTPException(400, "Chỉ nhận file Word .docx. Hãy mở đề trong Word, chọn Lưu thành .docx rồi tải lại.")
    data = await file.read()
    if len(data) > MAX_BYTES:
        raise HTTPException(413, "File quá lớn (tối đa 25 MB).")
    if not zipfile.is_zipfile(__import__("io").BytesIO(data)):
        raise HTTPException(400, "File không phải Word .docx hợp lệ.")
    eid = uuid.uuid4().hex[:12]
    d = _root() / eid
    d.mkdir(parents=True, exist_ok=True)
    safe = re.sub(r"[^\w.\- ]+", "_", name, flags=re.UNICODE).strip() or "de-thi.docx"
    src = d / "goc" / safe
    src.parent.mkdir(exist_ok=True)
    src.write_bytes(data)
    try:
        res = exam_shuffle.build_versions(src, d / "ket-qua", versions=versions, start_code=start_code, keep_order=keep_order, strip_marks=strip_marks, manual_answers=answers or None)
    except exam_shuffle.ExamError as e:
        shutil.rmtree(d, ignore_errors=True)
        raise HTTPException(400, str(e)) from e
    except Exception as e:  # file Word lạ làm thư viện lỗi: báo rõ thay vì 500 khó hiểu
        shutil.rmtree(d, ignore_errors=True)
        raise HTTPException(422, f"Không đọc được cấu trúc đề này ({type(e).__name__}). Hãy thử lưu lại đề bằng Word rồi tải lại.") from e
    zpath = d / "ket-qua" / f"{src.stem}-cac-ma-de.zip"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for f in [*res["files"], res["answer_key"]]:
            z.write(f, f.name)
    return {"id": eid, "summary": res["summary"], "files": [_entry(eid, f) for f in res["files"]], "answer_key": _entry(eid, res["answer_key"]),
            "zip": _entry(eid, zpath), "warnings": res["warnings"]}


@router.get("/exam/{eid}/file/{name}")
def download(eid: str, name: str):
    if not _ID.fullmatch(eid) or "/" in name or "\\" in name or name.startswith("."):
        raise HTTPException(404, "Không có file này")
    p = _root() / eid / "ket-qua" / name
    if not p.is_file():
        raise HTTPException(404, "Không có file này")
    return FileResponse(p, filename=name)
