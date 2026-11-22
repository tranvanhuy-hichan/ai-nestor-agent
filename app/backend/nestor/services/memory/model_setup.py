"""Background installation for local OCR and Ollama embedding models."""
import hashlib
import json
import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile
from threading import Lock, Thread

import httpx

from nestor.core import config
from . import embeddings, pdf_ocr

log = logging.getLogger(__name__)
_WINGET_ID = "UB-Mannheim.TesseractOCR"
_DATA_URL = "https://raw.githubusercontent.com/tesseract-ocr/tessdata_fast/65727574dfcd264acbb0c3e07860e4e9e9b22185"
_DATA_HASH = {
    "vie": "79df64caf7bcfb2a27df5042ecb6121e196eada34da774956995747636d5bfa1",
    "eng": "7d4322bd2a7749724879683fc3912cb542f19906c83bcc1a52132556427170b2",
}


class SetupError(RuntimeError):
    pass


class SetupJob:
    def __init__(self):
        self._lock = Lock()
        self._state = {"phase": "idle", "error": ""}

    def snapshot(self) -> dict:
        with self._lock:
            return dict(self._state)

    def update(self, **values) -> None:
        with self._lock:
            self._state.update(values)

    def start(self, operation, **details) -> bool:
        with self._lock:
            if self._state["phase"] == "running":
                return False
            self._state = {"phase": "running", "error": "", **details}

        def run():
            try:
                operation(self)
            except Exception as exc:
                log.info("Model setup failed: %s", exc)
                self.update(phase="error", error=str(exc)[:350])
            else:
                self.update(phase="done")

        try:
            Thread(target=run, daemon=True, name="nestor-model-setup").start()
        except RuntimeError:
            self.update(phase="error", error="Không khởi động được tác vụ cài đặt.")
            raise
        return True


ocr_job = SetupJob()
embedding_job = SetupJob()


def _ocr_platform() -> str:
    if sys.platform == "win32":
        return "windows"
    if sys.platform.startswith("linux"):
        return "linux"
    if sys.platform == "darwin":
        return "macos"
    return "other"


def _install_commands() -> list[list[str]]:
    platform = _ocr_platform()
    if platform == "windows":
        winget = shutil.which("winget")
        local_appdata = os.environ.get("LOCALAPPDATA")
        if not winget and local_appdata:
            candidate = Path(local_appdata) / "Microsoft" / "WindowsApps" / "winget.exe"
            if candidate.is_file():
                winget = str(candidate)
        if winget:
            return [[winget, "install", "--id", _WINGET_ID, "--exact", "--source", "winget", "--no-upgrade",
                     "--silent", "--disable-interactivity", "--accept-package-agreements", "--accept-source-agreements"]]
    elif platform == "linux":
        apt = shutil.which("apt-get")
        sudo = shutil.which("sudo")
        prefix = [] if os.geteuid() == 0 else [sudo, "-n"] if sudo else None
        if apt and prefix is not None:
            return [
                [*prefix, apt, "update"],
                [*prefix, apt, "install", "-y", "tesseract-ocr", "tesseract-ocr-vie", "tesseract-ocr-eng"],
            ]
    return []


def _probe_ocr() -> tuple[bool, set[str]]:
    try:
        executable = pdf_ocr.find_tesseract()
    except pdf_ocr.OcrError:
        return False, set()
    try:
        return True, pdf_ocr.installed_languages(executable)
    except pdf_ocr.OcrError:
        return True, set()


def ocr_status() -> dict:
    installed, languages = _probe_ocr()
    ready = set(_DATA_HASH) <= languages
    return {
        "platform": _ocr_platform(),
        "installed": installed,
        "languages": sorted(set(_DATA_HASH) & languages),
        "ready": ready,
        "can_install": not ready and (installed or bool(_install_commands())),
        "job": ocr_job.snapshot(),
    }


def _download_language(client: httpx.Client, target: Path, digest: str) -> None:
    path = None
    try:
        with NamedTemporaryFile(dir=target.parent, delete=False) as output:
            path = Path(output.name)
            sha = hashlib.sha256()
            size = 0
            with client.stream("GET", f"{_DATA_URL}/{target.name}") as response:
                response.raise_for_status()
                for chunk in response.iter_bytes():
                    size += len(chunk)
                    if size > 8 * 1024 * 1024:
                        raise SetupError("Tệp ngôn ngữ OCR vượt quá kích thước dự kiến.")
                    sha.update(chunk)
                    output.write(chunk)
        if sha.hexdigest() != digest:
            raise SetupError("Không xác minh được tệp ngôn ngữ OCR tải về.")
        path.replace(target)
    finally:
        if path is not None:
            path.unlink(missing_ok=True)


def install_ocr(job: SetupJob) -> None:
    installed, languages = _probe_ocr()
    if not installed:
        commands = _install_commands()
        if not commands:
            raise SetupError("Không tìm thấy trình quản lý gói phù hợp. Hãy làm theo hướng dẫn cài thủ công.")
        job.update(step="engine")
        try:
            for command in commands:
                subprocess.run(
                    command, check=True, timeout=900, stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                    env={**os.environ, "DEBIAN_FRONTEND": "noninteractive"},
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                )
        except (subprocess.SubprocessError, OSError) as exc:
            log.info("Tesseract installer: %s", exc)
            raise SetupError("Không cài được Tesseract. Kiểm tra quyền cài đặt và kết nối, hoặc dùng hướng dẫn thủ công.") from exc
        installed, languages = _probe_ocr()
        if not installed:
            raise SetupError("Đã chạy trình cài nhưng chưa tìm thấy Tesseract trên máy chủ.")
    if set(_DATA_HASH) <= languages:
        return
    job.update(step="languages")
    directory = pdf_ocr.managed_tessdata()
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    try:
        with httpx.Client(timeout=30) as client:
            for language, digest in _DATA_HASH.items():
                target = directory / f"{language}.traineddata"
                if target.is_file():
                    with target.open("rb") as existing:
                        if hashlib.file_digest(existing, "sha256").hexdigest() == digest:
                            continue
                _download_language(client, target, digest)
    except httpx.HTTPError as exc:
        raise SetupError("Không tải được dữ liệu OCR. Kiểm tra kết nối tới GitHub rồi thử lại.") from exc
    if not set(_DATA_HASH) <= _probe_ocr()[1]:
        raise SetupError("Tesseract chưa tải được cả hai bộ ngôn ngữ.")


def pull_embedding(job: SetupJob, model: str) -> None:
    endpoint = embeddings.ollama_url(config.load()).rstrip("/")
    try:
        with httpx.stream(
            "POST", f"{endpoint}/api/pull", json={"model": model, "stream": True},
            timeout=httpx.Timeout(180, connect=5), follow_redirects=False,
        ) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if not line:
                    continue
                entry = json.loads(line)
                if entry.get("error"):
                    raise SetupError(str(entry["error"]))
                if entry.get("status") == "success":
                    return
                total, completed = entry.get("total"), entry.get("completed")
                percent = min(100, max(0, round(100 * completed / total))) if isinstance(total, int) and total > 0 and isinstance(completed, int) else None
                job.update(percent=percent)
    except httpx.ConnectError as exc:
        raise SetupError("Không kết nối được với Ollama. Hãy khởi động Ollama rồi thử lại.") from exc
    except (httpx.HTTPError, ValueError) as exc:
        raise SetupError("Không tải được model từ Ollama. Kiểm tra Ollama và kết nối rồi thử lại.") from exc
    raise SetupError("Ollama đóng kết nối trước khi tải xong.")
