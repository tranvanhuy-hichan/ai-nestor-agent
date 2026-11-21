"""Banner thong tin he thong va dong chu ASCII lon cho CLI Nestor Agent."""
import os
import re
import shutil
import sys
from ..core.config import Config
from .ui import bold, cyan, dim, green, yellow, L

LOGO_LARGE = [
    "███╗   ██╗███████╗███████╗████████╗ ██████╗ ██████╗      █████╗  ██████╗ ███████╗███╗   ██╗████████╗",
    "████╗  ██║██╔════╝██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗    ██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝",
    "██╔██╗ ██║█████╗  ███████╗   ██║   ██║   ██║██████╔╝    ███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║   ",
    "██║╚██╗██║██╔══╝  ╚════██║   ██║   ██║   ██║██╔══██╗    ██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║   ",
    "██║ ╚████║███████╗███████║   ██║   ╚██████╔╝██║  ██║    ██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║   ",
    "╚═╝  ╚═══╝╚══════╝╚══════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝    ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝   ",
]

LOGO_COMPACT = [
    "███╗   ██╗███████╗███████╗████████╗ ██████╗ ██████╗ ",
    "████╗  ██║██╔════╝██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗",
    "██╔██╗ ██║█████╗  ███████╗   ██║   ██║   ██║██████╔╝",
    "██║╚██╗██║██╔══╝  ╚════██║   ██║   ██║   ██║██╔══██╗",
    "██║ ╚████║███████╗███████║   ██║   ╚██████╔╝██║  ██║",
    "╚═╝  ╚═══╝╚══════╝╚══════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝",
    "          ───  A G E N T  ───          ",
]

GRADIENT = [
    "\033[38;2;0;229;255m",
    "\033[38;2;45;156;240m",
    "\033[38;2;79;110;242m",
    "\033[38;2;114;90;242m",
    "\033[38;2;147;75;242m",
    "\033[38;2;168;85;247m",
    "\033[38;2;192;132;252m",
]
RESET = "\033[0m"
_ANSI_RE = re.compile(r"\033\[[0-9;]*m")


def _get_cols() -> int:
    cols = shutil.get_terminal_size(fallback=(80, 24)).columns
    try:
        env_cols = int(os.environ.get("COLUMNS", 0))
        if env_cols > 0:
            cols = env_cols
    except (ValueError, TypeError):
        pass
    return cols


def _vis_len(s: str) -> int:
    """Do dai thuc te cua chuoi khi hien thi tren terminal (da bo ma mau ANSI)."""
    return len(_ANSI_RE.sub("", s))


def _render_logo(cols: int) -> list[str]:
    buf = [""]
    if cols >= 104:
        for i, line in enumerate(LOGO_LARGE):
            c = GRADIENT[i % len(GRADIENT)]
            buf.append(f"{c}{line}{RESET}")
    elif cols >= 56:
        for i, line in enumerate(LOGO_COMPACT):
            c = GRADIENT[i % len(GRADIENT)]
            buf.append(f"{c}{line}{RESET}")
    else:
        buf.append(f"{bold(cyan('✦ NESTOR AGENT ✦'))}")
    return buf


def _make_box(title: str, rows: list[tuple[str, str]], tip: str, max_w: int = 80) -> str:
    cols = _get_cols()
    box_w = max(42, min(cols - 2, max_w))
    top = "┌" + "─" * (box_w - 2) + "┐"
    mid = "├" + "─" * (box_w - 2) + "┤"
    bot = "└" + "─" * (box_w - 2) + "┘"

    h_clean = title[:box_w - 4]
    pad_h = max(0, box_w - 2 - _vis_len(h_clean))
    header = f"{h_clean}{' ' * pad_h}"

    buf = ["", dim(top), f"{dim('│')}{bold(header)}{dim('│')}", dim(mid)]

    for left, right in rows:
        pad = max(1, box_w - 2 - _vis_len(left) - _vis_len(right))
        line = f"{left}{' ' * pad}{right}"
        buf.append(f"{dim('│')}{line}{dim('│')}")

    tip_clean = tip[:box_w - 4]
    pad_tip = max(0, box_w - 2 - _vis_len(tip_clean))
    line_tip = f"{tip_clean}{' ' * pad_tip}"
    buf.append(dim(mid))
    buf.append(f"{dim('│')}{dim(line_tip)}{dim('│')}")
    buf.append(dim(bot))
    return "\n".join(buf)


def _get_skills_count(cfg: Config | None = None) -> int:
    try:
        from ..services import skills as skillmod
        if cfg is None:
            from ..core import config as cfgmod
            cfg = cfgmod.load()
        return len(skillmod.discover(cfg))
    except Exception:
        return 0


def print_chat_banner(cfg: Config, provider: str, perm: str, sid: str | None = None) -> None:
    """In dong chu NESTOR lon va khung thong tin he thong khi khoi dong `nestor chat`."""
    cols = _get_cols()
    skills_count = _get_skills_count(cfg)
    pcfg = cfg.providers.get(provider)
    model_str = f"{provider} · {pcfg.model if pcfg else 'unknown'}"
    if len(model_str) > 34:
        model_str = model_str[:31] + "…"

    sess_disp = (sid[:18] + "…") if sid and len(sid) > 18 else (sid or (L("Mới", "New")))
    perm_color = yellow(perm) if perm != "full" else "\033[31mfull (no confirm)\033[0m"

    title = L("  Nestor Agent v0.6.3 · Trợ lý AI cá nhân & Tự hành", "  Nestor Agent v0.6.3 · Local-first Personal AI Assistant")
    rows = [
        (f"  {L('Mô hình', 'Model')}:   {cyan(model_str)}", f"{L('Kỹ năng', 'Skills')}:   {green(f'{skills_count} loaded')}  "),
        (f"  {L('Quyền', 'Access')}:   {perm_color}", f"{L('Phiên', 'Session')}:  {sess_disp}  "),
    ]
    tip = L("  Gõ /help để xem lệnh · /skills xem kỹ năng · Ctrl+D để thoát", "  Type /help for commands · /skills to view skills · Ctrl+D to exit")

    box_limit = 100 if cols >= 104 else 80
    output = "\n".join(_render_logo(cols)) + "\n" + _make_box(title, rows, tip, max_w=box_limit) + "\n"
    sys.stdout.write(output)
    sys.stdout.flush()


def print_onboard_banner(cfg: Config | None = None) -> None:
    """In dong chu NESTOR lon va khung huong dan khi chay `nestor onboard`."""
    cols = _get_cols()
    if cfg is None:
        try:
            from ..core import config as cfgmod
            cfg = cfgmod.load()
        except Exception:
            cfg = None
    skills_count = _get_skills_count(cfg)
    data_dir = str(cfg.workspace_path().parent) if cfg else "user-data"
    if len(data_dir) > 34:
        data_dir = "…" + data_dir[-31:]

    title = L("  Nestor Agent v0.6.3 · Trình hướng dẫn cài đặt (Setup Wizard)", "  Nestor Agent v0.6.3 · Setup Wizard")
    rows = [
        (f"  {L('Dữ liệu', 'Data')}:   {cyan(data_dir)}", f"{L('Kỹ năng', 'Skills')}:   {green(f'{skills_count} loaded')}  "),
        (f"  {L('Cổng', 'Port')}:     8787", "URL:      http://127.0.0.1:8787  "),
    ]
    tip = L("  Dùng phím ↑/↓ và Enter để chọn · Space để đánh dấu chọn", "  Use ↑/↓ and Enter to select · Space to toggle")

    box_limit = 100 if cols >= 104 else 80
    output = "\n".join(_render_logo(cols)) + "\n" + _make_box(title, rows, tip, max_w=box_limit) + "\n"
    sys.stdout.write(output)
    sys.stdout.flush()


def print_open_banner(url: str, cfg: Config | None = None) -> None:
    """In dong chu NESTOR lon va khung thong tin khi chay `nestor open`."""
    cols = _get_cols()
    if cfg is None:
        try:
            from ..core import config as cfgmod
            cfg = cfgmod.load()
        except Exception:
            cfg = None
    skills_count = _get_skills_count(cfg)
    prov = (cfg.default_provider if cfg else "unknown") or "unknown"
    pcfg = cfg.providers.get(prov) if cfg else None
    model_str = f"{prov} · {pcfg.model if pcfg else 'unknown'}"
    if len(model_str) > 34:
        model_str = model_str[:31] + "…"

    title = L("  Nestor Agent v0.6.3 · Mở Giao diện Web (Web UI)", "  Nestor Agent v0.6.3 · Web UI")
    rows = [
        (f"  {L('Địa chỉ', 'URL')}:   {cyan(url)}", f"{L('Trạng thái', 'Status')}:  {green(L('Đang chạy', 'Running'))}  "),
        (f"  {L('Mô hình', 'Model')}: {model_str}", f"{L('Kỹ năng', 'Skills')}:   {green(f'{skills_count} loaded')}  "),
    ]
    tip = L("  Đang mở trình duyệt web...", "  Opening web browser...")

    box_limit = 100 if cols >= 104 else 80
    output = "\n".join(_render_logo(cols)) + "\n" + _make_box(title, rows, tip, max_w=box_limit) + "\n"
    sys.stdout.write(output)
    sys.stdout.flush()
