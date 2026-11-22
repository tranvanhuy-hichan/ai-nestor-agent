"""Local OCR for image-only PDF pages. Word boxes use coordinates relative to the rendered page."""
import csv
import io
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from threading import Lock

from nestor.core import paths

_page_slot = Lock()


class OcrError(RuntimeError):
    pass


def find_tesseract() -> str:
    executable = shutil.which("tesseract")
    if executable:
        return executable
    if sys.platform == "win32":
        for variable in ("ProgramFiles", "ProgramW6432", "ProgramFiles(x86)", "LOCALAPPDATA"):
            root = os.environ.get(variable)
            if root:
                base = Path(root)
                for directory in (base, base / "Programs") if variable == "LOCALAPPDATA" else (base,):
                    path = directory / "Tesseract-OCR" / "tesseract.exe"
                    if path.is_file():
                        return str(path)
    if sys.platform == "darwin":
        for directory in ("/opt/homebrew/bin", "/usr/local/bin"):
            path = Path(directory) / "tesseract"
            if path.is_file():
                return str(path)
    raise OcrError("chưa cài Tesseract trên máy chạy Nestor")


def _run(args: list[str], *, data: bytes | None = None, timeout: int = 10) -> str:
    try:
        result = subprocess.run(
            args, input=data, capture_output=True, timeout=timeout,
            env={**os.environ, "OMP_THREAD_LIMIT": "2"},
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    except subprocess.TimeoutExpired as exc:
        raise OcrError("quá thời gian nhận dạng cho một trang") from exc
    except OSError as exc:
        raise OcrError("không chạy được Tesseract") from exc
    if result.returncode:
        raise OcrError("Tesseract không đọc được trang hoặc bộ ngôn ngữ")
    return result.stdout.decode("utf-8", errors="replace")


def managed_tessdata() -> Path:
    return paths.DATA / "ocr" / "tessdata"


def _language_args() -> list[str]:
    directory = managed_tessdata()
    if all((directory / f"{lang}.traineddata").is_file() for lang in ("eng", "vie")):
        return ["--tessdata-dir", str(directory.resolve())]
    return []


def installed_languages(executable: str) -> set[str]:
    return set(_run([executable, *_language_args(), "--list-langs"]).splitlines())


@dataclass(frozen=True)
class OcrEngine:
    executable: str
    language: str

    @classmethod
    def detect(cls):
        executable = find_tesseract()
        available = installed_languages(executable)
        language = "+".join(lang for lang in ("vie", "eng") if lang in available)
        if not language:
            raise OcrError("Tesseract thiếu bộ ngôn ngữ vie và eng")
        return cls(executable, language)

    def read_page(self, path: Path, index: int) -> list[dict]:
        import pypdfium2 as pdfium

        with _page_slot:
            with pdfium.PdfDocument(path) as doc:
                page = doc[index]
                width, height = page.get_size()
                scale = min(300 / 72, 3600 / max(width, height))
                with io.BytesIO() as image:
                    bitmap = page.render(scale=scale, grayscale=True)
                    try:
                        bitmap.to_pil().save(image, format="PNG")
                        width_px, height_px = bitmap.width, bitmap.height
                    finally:
                        bitmap.close()
                    data = image.getvalue()
            tsv = _run([self.executable, "stdin", "stdout", *_language_args(), "-l", self.language, "tsv"], data=data, timeout=45)
        return _words(tsv, width_px, height_px)


def _words(tsv: str, width: int, height: int) -> list[dict]:
    words = []
    previous_line = None
    for row in csv.DictReader(io.StringIO(tsv), delimiter="\t", quoting=csv.QUOTE_NONE):
        text = (row.get("text") or "").strip()
        if row.get("level") != "5" or not text:
            continue
        line = (row["block_num"], row["par_num"], row["line_num"])
        if previous_line is not None:
            text = (" " if line == previous_line else "\n") + text
        previous_line = line
        x, y, w, h = (int(row[key]) for key in ("left", "top", "width", "height"))
        words.append({"text": text, "x": x / width, "y": y / height, "width": w / width, "height": h / height})
    return words
