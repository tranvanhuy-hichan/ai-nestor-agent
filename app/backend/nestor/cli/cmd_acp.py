"""Lenh `nestor acp`: Chay Nestor Agent duoi dang ACP (Agent Client Protocol) server
cho phep ket noi truc tiep vao cac trinh soan thao nhu Cursor, Zed, Windsurf, Neovim.
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path


def run_acp(argv: list[str] | None = None) -> int:
    # 1. Kiem tra binary hermes-acp san co tren may
    user_acp = Path.home() / ".local" / "bin" / "hermes-acp"
    system_acp = shutil.which("hermes-acp") or (str(user_acp) if user_acp.is_file() else None)

    if system_acp and os.access(system_acp, os.X_OK):
        # Chuyen tiep thang sang hermes-acp runtime
        cmd = [system_acp, *(argv or [])]
        try:
            return subprocess.call(cmd)
        except KeyboardInterrupt:
            return 0

    # 2. Hoac chay qua Python module neu co san package acp
    hermes_repo = Path.home() / "Projects" / "oss" / "hermes-agent"
    if hermes_repo.is_dir():
        script = hermes_repo / "acp_adapter" / "entry.py"
        if script.is_file():
            env = os.environ.copy()
            env["PYTHONPATH"] = f"{hermes_repo}:{env.get('PYTHONPATH', '')}"
            cmd = [sys.executable, str(script), *(argv or [])]
            try:
                return subprocess.call(cmd, env=env)
            except KeyboardInterrupt:
                return 0

    print("Chưa tìm thấy ACP adapter runtime. Hãy đảm bảo hermes-agent hoặc acp đã được cài đặt.", file=sys.stderr)
    return 1


def register(sub) -> None:
    from .ui import L
    s = sub.add_parser("acp", help=L("chạy agent dưới dạng ACP stdio server cho Cursor, Zed, Windsurf", "run agent as an ACP stdio server for Cursor, Zed, Windsurf"))
    s.add_argument("acp_args", nargs="*", help="args for acp")
    s.set_defaults(func=lambda args: run_acp(getattr(args, "acp_args", [])))

