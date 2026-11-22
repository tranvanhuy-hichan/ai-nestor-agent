"""Banner thong tin he thong va dong chu ASCII lon cho CLI Nestor Agent."""
import re
import shutil
import sys

from rich.cells import cell_len, chop_cells

from ..core.config import Config
from .ui import L, bold, cyan, dim, green, paint, yellow

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
    "38;2;0;229;255",
    "38;2;45;156;240",
    "38;2;79;110;242",
    "38;2;114;90;242",
    "38;2;147;75;242",
    "38;2;168;85;247",
    "38;2;192;132;252",
]
_ANSI_RE = re.compile(r"\033\[[0-9;]*m")


def _center(line: str, cols: int) -> str:
    width = cell_len(_ANSI_RE.sub("", line))
    return " " * max(0, (cols - width) // 2) + line


def _render_logo(cols: int) -> list[str]:
    if cols >= 104:
        logo = LOGO_LARGE
    elif cols >= 56:
        logo = LOGO_COMPACT
    else:
        label = "✦ NESTOR AGENT ✦" if cols >= 16 else "NESTOR AGENT"
        return [_center(bold(cyan(line)), cols) for line in chop_cells(label, cols)]

    logo_width = max(map(len, logo))
    rail_width = min(22, (cols - logo_width) // 2 - 4)
    middle = (len(logo) - 1) // 2
    lines = []
    for i, line in enumerate(logo):
        if logo is LOGO_COMPACT and i == len(logo) - 1:
            line = line.strip().center(logo_width)
        line = paint(GRADIENT[i], line.ljust(logo_width))
        if rail_width >= 8 and abs(i - middle) <= 1:
            trace = "·" * (rail_width // 2 - 2)
            if i == middle:
                left, right = "✦" + "━" * (rail_width - 2) + "╴", "╶" + "━" * (rail_width - 2) + "✦"
            else:
                left, right = f"◇ {trace}", f"{trace} ◇"
            line = f"{paint(GRADIENT[i], left.rjust(rail_width))}   {line}   {paint(GRADIENT[i], right.ljust(rail_width))}"
        lines.append(_center(line, cols))
    return lines


def _make_box(title: str, rows: list[tuple[str, str]], tip: str, cols: int) -> list[str]:
    box_limit = 100 if cols >= 104 else 80
    box_w = min(box_limit, cols - 2)
    inner_w = box_w - 2
    rule = "─" * inner_w

    def edge(text: str) -> str:
        return paint("38;5;61", text)

    def framed(content: str) -> str:
        pad = inner_w - cell_len(_ANSI_RE.sub("", content))
        return f"{edge('│')}{content}{' ' * pad}{edge('│')}"

    lines = [edge(f"╭{rule}╮")]
    lines.extend(framed(paint("1;96", part)) for part in chop_cells(title, inner_w))
    lines.append(edge(f"├{rule}┤"))

    for left, right in rows:
        pad = inner_w - cell_len(_ANSI_RE.sub("", left + right))
        if right and pad >= 3:
            lines.append(framed(f"{left}{' ' * pad}{right}"))
        else:
            for content in (left.rstrip(), "  " + right.rstrip()):
                plain = _ANSI_RE.sub("", content)
                if not plain.strip():
                    continue
                parts = [content] if cell_len(plain) <= inner_w else chop_cells(plain, inner_w)
                lines.extend(framed(part) for part in parts)

    lines.append(edge(f"├{rule}┤"))
    lines.extend(framed(dim(part)) for part in chop_cells(tip, inner_w))
    lines.append(edge(f"╰{rule}╯"))
    return [_center(line, cols) for line in lines]


def print_status_card(title: str, rows: list[tuple[str, str]], tip: str) -> None:
    cols = max(1, shutil.get_terminal_size(fallback=(80, 24)).columns)
    print("\n".join(["", *_render_logo(cols), ""]))
    if cols < 24:
        print(title.strip())
        for left, right in rows:
            print(left.strip())
            if right:
                print(right.strip())
        print(tip.strip())
        return
    print("\n".join(_make_box(title, rows, tip, cols)))


def _print_banner(title: str, rows: list[tuple[str, str]], tip: str) -> None:
    cols = max(1, shutil.get_terminal_size(fallback=(80, 24)).columns)
    lines = ["", *_render_logo(cols)]
    if cols >= 8:
        lines.extend(["", *_make_box(title, rows, tip, cols)])
    sys.stdout.write("\n".join(lines) + "\n")
    sys.stdout.flush()


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
    skills_count = _get_skills_count(cfg)
    pcfg = cfg.providers.get(provider)
    model_str = f"{provider} · {pcfg.model if pcfg else 'unknown'}"
    sess_disp = (sid[:18] + "…") if sid and len(sid) > 18 else (sid or (L("Mới", "New")))
    perm_color = yellow(perm) if perm != "full" else paint("31", "full (no confirm)")

    title = L("  ✦  Nestor Agent v0.7.3  /  Trò chuyện", "  ✦  Nestor Agent v0.7.3  /  Chat")
    rows = [
        (f"  {dim(L('Mô hình', 'Model'))}  {bold(cyan(model_str))}", f"{green(str(skills_count))} {L('kỹ năng', 'skills')}  "),
        (f"  {dim(L('Quyền', 'Access'))}    {perm_color}", f"{dim(L('Phiên', 'Session'))}  {sess_disp}  "),
    ]
    tip = L("  /help  Lệnh   ·   /skills  Kỹ năng   ·   Ctrl+D  Thoát", "  /help  Commands   ·   /skills  Skills   ·   Ctrl+D to exit")

    _print_banner(title, rows, tip)


def print_onboard_banner(cfg: Config | None = None) -> None:
    """In dong chu NESTOR lon va khung huong dan khi chay `nestor onboard`."""
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

    title = L("  Nestor Agent v0.7.3 · Trình hướng dẫn cài đặt (Setup Wizard)", "  Nestor Agent v0.7.3 · Setup Wizard")
    rows = [
        (f"  {L('Dữ liệu', 'Data')}:   {cyan(data_dir)}", f"{L('Kỹ năng', 'Skills')}:   {green(f'{skills_count} loaded')}  "),
        (f"  {L('Cổng', 'Port')}:     8787", "URL:      http://127.0.0.1:8787  "),
    ]
    tip = L("  Dùng phím ↑/↓ và Enter để chọn · Space để đánh dấu chọn", "  Use ↑/↓ and Enter to select · Space to toggle")

    _print_banner(title, rows, tip)


def print_open_banner(url: str, cfg: Config | None = None) -> None:
    """In dong chu NESTOR lon va khung thong tin khi chay `nestor open`."""
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

    title = L("  Nestor Agent v0.7.3 · Mở Giao diện Web (Web UI)", "  Nestor Agent v0.7.3 · Web UI")
    rows = [
        (f"  {L('Địa chỉ', 'URL')}:   {cyan(url)}", f"{L('Trạng thái', 'Status')}:  {green(L('Đang chạy', 'Running'))}  "),
        (f"  {L('Mô hình', 'Model')}: {model_str}", f"{L('Kỹ năng', 'Skills')}:   {green(f'{skills_count} loaded')}  "),
    ]
    tip = L("  Đang mở trình duyệt web...", "  Opening web browser...")

    _print_banner(title, rows, tip)
