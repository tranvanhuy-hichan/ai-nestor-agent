"""Render Office files with an isolated LibreOffice profile for the document viewer."""
import os
import shutil
import subprocess
import sys
from pathlib import Path
from threading import BoundedSemaphore

FORMATS = frozenset({".doc", ".docx", ".odt", ".xls", ".xlsx", ".xlsm", ".ods", ".ppt", ".pptx", ".odp"})
_slots = BoundedSemaphore(2)

# Disable macros and automatic document-link updates in the temporary profile.
_PROFILE = """<?xml version="1.0" encoding="UTF-8"?>
<oor:items xmlns:oor="http://openoffice.org/2001/registry">
 <item oor:path="/org.openoffice.Office.Common/Security/Scripting">
  <prop oor:name="MacroSecurityLevel" oor:op="fuse"><value>3</value></prop>
  <prop oor:name="BlockUntrustedRefererLinks" oor:op="fuse"><value>true</value></prop>
  <prop oor:name="DisableMacrosExecution" oor:op="fuse"><value>true</value></prop>
 </item>
 <item oor:path="/org.openoffice.Office.Writer/Content/Update">
  <prop oor:name="Link" oor:op="fuse"><value>2</value></prop>
 </item>
 <item oor:path="/org.openoffice.Office.Calc/Content/Update">
  <prop oor:name="Link" oor:op="fuse"><value>1</value></prop>
 </item>
</oor:items>
"""


class PreviewError(RuntimeError):
    pass


def _find_soffice() -> str | None:
    if sys.platform != "win32":
        return shutil.which("soffice") or shutil.which("libreoffice")
    # The console launcher waits for the headless conversion to finish.
    on_path = shutil.which("soffice.com")
    if on_path:
        return on_path
    for variable in ("ProgramFiles", "ProgramW6432", "ProgramFiles(x86)"):
        root = os.environ.get(variable)
        if root:
            launcher = Path(root) / "LibreOffice" / "program" / "soffice.com"
            if launcher.is_file():
                return str(launcher)
    return None


def render_office_pdf(source: Path, ext: str, work: Path) -> Path:
    if ext not in FORMATS:
        raise PreviewError("Định dạng Office này chưa hỗ trợ xem trước.")
    soffice = _find_soffice()
    if not soffice:
        raise PreviewError("Máy chủ cần LibreOffice để hiển thị bố cục của tệp Office.")
    if not _slots.acquire(timeout=5):
        raise PreviewError("Máy chủ đang tạo bản xem trước khác. Hãy thử lại.")
    try:
        profile = work / "profile"
        (profile / "user").mkdir(parents=True)
        (profile / "user" / "registrymodifications.xcu").write_text(_PROFILE, encoding="utf-8")
        staged = work / f"document{ext}"
        shutil.copyfile(source, staged)
        try:
            result = subprocess.run(
                [soffice, f"-env:UserInstallation={profile.as_uri()}", "--headless", "--norestore",
                 "--convert-to", "pdf", "--outdir", str(work), str(staged)],
                cwd=work, env={**os.environ, "HOME": str(work)}, stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60, check=False,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise PreviewError("LibreOffice không thể tạo bản xem trước trong thời gian cho phép.") from exc
        pdf = work / "document.pdf"
        if result.returncode != 0 or not pdf.is_file():
            raise PreviewError("LibreOffice không mở được tài liệu. Tệp có thể bị hỏng hoặc có mật khẩu.")
        return pdf
    finally:
        _slots.release()
