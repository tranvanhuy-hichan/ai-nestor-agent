"""Banner thong tin he thong va dong chu ASCII lon cho CLI Nestor Agent."""
import re
import shutil
import sys
from itertools import zip_longest

from rich.cells import cell_len, chop_cells
from rich.console import Console
from rich.text import Text

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

# Alpha silhouette of app/frontend/src/assets/nestor-mark.png in Braille cells.
OWL_LOGO = (
    "⢳⣄      ⣀⣀      ⣠⡞",
    "⠈⢿⣷⣦⣄⠠⣾⣿⣿⣿⣿⣷⠄⣠⣴⣾⡿⠁",
    " ⠈⣛⢿⣿⣷⣜⣿⣿⣿⣿⣣⣾⣿⡿⣛⠁",
    " ⣼⣿⠃⣌⠻⢿⣿⣿⣿⣿⡿⠟⣡ ⣿⣧",
    "⢰⠿⣿⡄⢻⣷⣄⠙⢿⡿⠋⣠⣾⡟⢠⣿⠿⡆",
    "⠁ ⢻⣷⡀⠛⠟⢷⡌⢡⡾⠻⠛⢀⣾⡿ ⠈",
    "  ⠈⠙⠿⣦⡀⠈⣷⣾⠁⢀⣴⠿⠋⠁",
    "      ⠁ ⠸⠇ ⠈",
)

OWL_LOGO_LARGE = (
    "⢳⣄                      ⣠⡞",
    "⠈⣿⣷⣤⡀    ⣀⣤⣶⣶⣶⣶⣤⣀    ⢀⣠⣾⣿⠃",
    " ⠸⣿⣿⣿⣶⣄⡀⠺⣿⣿⣿⣿⣿⣿⣿⣿⠟⢀⣠⣶⣿⣿⣿⠏",
    "  ⠙⠻⣿⣿⣿⣿⣦⡙⣿⣿⣿⣿⣿⣿⢋⣴⣿⣿⣿⣿⠟⠋",
    "  ⢰⣷⣄⠙⠿⣿⣿⣿⣾⣿⣿⣿⣿⣿⣿⣿⣿⠿⠋⢡⣾⣆",
    " ⢠⣿⣿⡇ ⣦⡈⠛⢿⣿⣿⣿⣿⣿⣿⡿⠛⢁⣴ ⢸⣿⣿⡄",
    " ⣾⣿⣿⡇ ⣿⣿⣦⡀⠙⢿⣿⣿⡿⠋⢀⣴⣿⣿ ⢸⣿⣿⣷",
    "⡸⠋ ⣿⣿⡀⠘⣿⣿⣿⣦ ⠻⠟ ⣴⣿⣿⣿⠃⢀⣿⣿ ⠙⢇",
    "   ⢹⣿⣷⡄⠈⠙⠛⠻⣷⡀⢀⣾⠟⠛⠋⠁⢀⣾⣿⡟",
    "   ⠈⠛⠿⣿⣦⡀  ⢹⣷⣼⡏  ⢀⣴⣿⠿⠛⠁",
    "       ⠙⠳⠄  ⢿⡿  ⢠⠞⠋",
    "            ⠸⠇",
)

OWL_LOGO_WIDE = (
    "⢳⣄                              ⣠⡞",
    "⠈⣿⣷⣄          ⢀⣀⣀⣀⣀⡀          ⣠⣾⣿⠃",
    " ⢹⣿⣿⣿⣦⣀   ⢀⣠⣶⣿⣿⣿⣿⣿⣿⣿⣿⣶⣄⡀   ⣀⣴⣾⣿⣿⡏",
    "  ⢻⣿⣿⣿⣿⣷⣦⣀⠙⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠋⣀⣴⣾⣿⣿⣿⣿⡟",
    "   ⠙⢿⣿⣿⣿⣿⣿⣷⣄⠹⣿⣿⣿⣿⣿⣿⣿⣿⠏⣠⣾⣿⣿⣿⣿⣿⡿⠛",
    "   ⢠⣦⡉⠻⢿⣿⣿⣿⣿⣷⣹⣿⣿⣿⣿⣿⣿⣏⣼⣿⣿⣿⣿⣿⠟⢉⣴⡄",
    "  ⢀⣾⣿⣿  ⠙⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⠋  ⣿⣿⣿⡀",
    "  ⣼⣿⣿⣿  ⣶⣄⠈⠛⢿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠛⠁⣠⣶  ⣿⣿⣿⣷",
    " ⣸⣿⣿⣿⣿  ⣿⣿⣷⣄ ⠙⢿⣿⣿⣿⣿⡿⠋ ⣠⣾⣿⣿  ⣿⣿⣿⣿⣇",
    "⢀⣿⠟⠉⣿⣿⡄ ⢹⣿⣿⣿⣷⡀ ⠹⣿⣿⠏ ⢀⣾⣿⣿⣿⡟ ⢠⣿⣿⠉⠻⣿⡄",
    "⠘⠁  ⣿⣿⣷⡀ ⠹⣿⣿⣿⣿⣦ ⠘⠃ ⣴⣿⣿⣿⣿⠟ ⢀⣾⣿⣿  ⠈⠓",
    "    ⢸⣿⣿⣷⣄  ⠉⠉⠉⢿⣷  ⣼⡿⠉⠉⠉  ⣠⣾⣿⣿⡏",
    "     ⠛⠿⣿⣿⣦⡀   ⠘⣿⣧⣸⣿⠃   ⢀⣴⣿⣿⠿⠛",
    "       ⠈⠙⠻⣿⣄   ⢹⣿⣿⡏   ⣠⣿⠟⠋⠁",
    "           ⠉⠂   ⢿⡿   ⠐⠉",
    "                ⠸⠇",
)

STAR_CLUSTER = (
    "    ·                ◇",
    "           ╭─────╮",
    "   ✧ ──────┤  ✦  ├────── ✧",
    "           ╰─────╯",
    "    ◇                ·",
)

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


def _make_box(
    title: str, rows: list[tuple[str, str]], tip: str, cols: int, *, sidebar: tuple[str, ...] = (), sidebar_path: tuple[str, str] | None = None,
    stars_row: int | None = None, wrap_sidebar_path: bool = False,
) -> list[str]:
    title = title.strip()
    fields = [(left.strip(), right.strip()) for left, right in rows]
    if cols < 24:
        path = [banner_field(*sidebar_path)] if sidebar_path else []
        return [title, *sidebar, *path, *(field for row in fields for field in row if field), tip.strip()]

    inner_w = min(160, cols - 2) - 2
    content_w = inner_w - 4
    owl = OWL_LOGO
    if cols >= 125:
        owl = OWL_LOGO_WIDE
    elif cols >= 104:
        owl = OWL_LOGO_LARGE
    owl_w = max(map(cell_len, owl))
    side_by_side = content_w >= owl_w + 4 + 32
    sidebar_w = max(owl_w, min(content_w * 29 // 100, content_w - 36)) if side_by_side else content_w
    details_w = content_w - sidebar_w - 4 if side_by_side else content_w
    border = GRADIENT[4]

    def framed(content: str) -> str:
        pad = inner_w - cell_len(_ANSI_RE.sub("", content))
        return f"{paint(border, '│')}{content}{' ' * pad}{paint(border, '│')}"

    console = Console(force_terminal=True, color_system="truecolor")

    def wrap(text: str, width: int) -> list[str]:
        lines = Text.from_ansi(text).wrap(console, width, overflow="fold")
        with console.capture() as capture:
            for line in lines:
                console.print(line, soft_wrap=True)
        return capture.get().splitlines()

    details = []
    for left, right in fields:
        combined = "   ".join(field for field in (left, right) if field)
        if cell_len(_ANSI_RE.sub("", combined)) <= details_w:
            details.append(combined)
        else:
            for field in (left, right):
                if not field:
                    continue
                plain = _ANSI_RE.sub("", field)
                details.extend([field] if cell_len(plain) <= details_w else wrap(field, details_w))

    owl_indent = " " * ((sidebar_w - owl_w) // 2)
    sidebar_lines = [
        owl_indent + paint(GRADIENT[i * (len(GRADIENT) - 1) // (len(owl) - 1)], line)
        for i, line in enumerate(owl)
    ]
    if sidebar or sidebar_path:
        sidebar_lines.append("")
        for text in sidebar:
            plain = _ANSI_RE.sub("", text)
            sidebar_lines.extend([text] if cell_len(plain) <= sidebar_w else wrap(text, sidebar_w))

    if sidebar_path:
        label, path = sidebar_path
        budget = sidebar_w - cell_len(label + ": ")
        if wrap_sidebar_path and cell_len(path) > budget:
            if budget < 2:
                sidebar_lines.extend(wrap(f"{label}:", sidebar_w))
                sidebar_lines.extend(chop_cells(path, sidebar_w))
            else:
                first = chop_cells(path, budget)[0]
                sidebar_lines.append(banner_field(label, first))
                sidebar_lines.extend(chop_cells(path[len(first):], sidebar_w))
        else:
            if cell_len(path) > budget:
                while path and cell_len(path) >= budget:
                    path = path[1:]
                path = "…" + path
            sidebar_lines.append(banner_field(label, path))

    if tip.strip():
        footer = [dim(line) for line in wrap(tip.strip(), details_w)]
        gap = max(1, len(sidebar_lines) - len(details) - len(footer)) if side_by_side else 1
        details.extend([""] * gap + footer)

    if side_by_side:
        body = [
            "  " + mark + " " * (sidebar_w + 4 - cell_len(_ANSI_RE.sub("", mark))) + detail
            for mark, detail in zip_longest(sidebar_lines, details, fillvalue="")
        ]
    else:
        body = ["  " + line for line in sidebar_lines]
        body.extend(["", *("  " + line for line in details)])

    if stars_row is not None and cols >= 125:
        art_w = max(map(cell_len, STAR_CLUSTER))
        art_start = inner_w - art_w - 6
        region = body[stars_row:stars_row + len(STAR_CLUSTER)]
        occupied = [cell_len(_ANSI_RE.sub("", line.rstrip())) for line in region]
        if len(occupied) == len(STAR_CLUSTER) and max(occupied) + 4 <= art_start:
            for i, art in enumerate(STAR_CLUSTER):
                gap = " " * (art_start - occupied[i])
                body[stars_row + i] = region[i].rstrip() + gap + paint(GRADIENT[i + 1], art)

    if cell_len(title) + 4 <= inner_w:
        left = (inner_w - cell_len(title) - 2) // 2
        right = inner_w - cell_len(title) - 2 - left
        heading = paint(border, "╭" + "─" * left)
        heading += f" {banner_heading(title)} "
        heading += paint(border, "─" * right + "╮")
    else:
        heading = paint(border, "╭" + "─" * inner_w + "╮")
        body[:0] = [*(f"  {banner_heading(line)}" for line in wrap(title, content_w)), ""]

    lines = [heading, framed(""), *(framed(line) for line in body), framed("")]
    lines.append(paint(border, "╰" + "─" * inner_w + "╯"))
    return [_center(line, cols) for line in lines]


def banner_heading(text: str) -> str:
    return paint("1;" + GRADIENT[0], text)


def banner_field(label: str, value: str) -> str:
    return f"{paint(GRADIENT[1], label + ':')} {value}"


def print_banner(
    title: str, rows: list[tuple[str, str]], tip: str, *, sidebar: tuple[str, ...] = (), sidebar_path: tuple[str, str] | None = None,
    stars_row: int | None = None, wrap_sidebar_path: bool = False,
) -> None:
    cols = max(1, shutil.get_terminal_size(fallback=(80, 24)).columns)
    lines = ["", *_render_logo(cols), "", *_make_box(title, rows, tip, cols, sidebar=sidebar, sidebar_path=sidebar_path, stars_row=stars_row, wrap_sidebar_path=wrap_sidebar_path)]
    sys.stdout.write("\n".join(lines) + "\n")
    sys.stdout.flush()


def _discover_skills(cfg: Config | None = None) -> dict:
    try:
        from ..services import skills

        if cfg is None:
            from ..core import config as cfgmod

            cfg = cfgmod.load()
        return skills.discover(cfg)
    except Exception:
        return {}


def _skill_categories(cfg: Config) -> dict[str, list[str]]:
    categories: dict[str, list[str]] = {}
    for skill in sorted(_discover_skills(cfg).values(), key=lambda skill: skill.name):
        if skill.active and not skill.bundled:
            categories.setdefault(skill.category, []).append(skill.name)

    return categories


def available_skill_rows(cfg: Config, *, max_categories: int, compact: bool = False) -> list[str]:
    categories = _skill_categories(cfg)
    count = sum(map(len, categories.values()))
    if compact:
        value = L(f"{count} trong {len(categories)} danh mục", f"{count} across {len(categories)} categories")
        rows = [banner_field(L("Kỹ năng khả dụng", "Available skills"), f"{value} · nestor skills list")]
    else:
        rows = [banner_heading(L(f"Kỹ năng khả dụng ({count})", f"Available skills ({count})"))]

    ordered = sorted(categories, key=lambda category: (-len(categories[category]), category))[:max_categories]
    for category in ordered:
        names = categories[category]
        preview = ", ".join(names[:3])
        if len(names) > 3:
            preview += L(f", +{len(names) - 3} kỹ năng", f", +{len(names) - 3} more")
        rows.append(banner_field(category, preview))
    remaining = len(categories) - len(ordered)
    if remaining and not compact:
        rows.append(dim(L(f"+{remaining} danh mục · /skills", f"+{remaining} categories · /skills")))
    return rows


def document_processing_rows(cfg: Config) -> list[str]:
    from ..services.memory.model_setup import ocr_status

    memory = cfg.memory
    embedding = L("Tắt", "Off") if memory.embeddings == "off" else " · ".join(
        part for part in (memory.embeddings, memory.provider, memory.model) if part
    )

    ocr = ocr_status()
    if not ocr["installed"]:
        ocr_description = L("Chưa cài Tesseract", "Tesseract not installed")
    else:
        languages = ", ".join(ocr["languages"])
        ocr_description = f"Tesseract ({languages})" if languages else "Tesseract"
        if not ocr["ready"]:
            ocr_description += L(" · Thiếu gói ngôn ngữ", " · Missing language packs")

    return [banner_field("Embedding", embedding), banner_field("OCR", ocr_description)]


def print_chat_banner(cfg: Config, provider: str, perm: str, sid: str | None = None) -> None:
    """In dong chu NESTOR lon va khung thong tin he thong khi khoi dong `nestor chat`."""
    from . import daemon

    state = daemon.read_state()
    host = state.get("host", daemon.default_host())
    port = state.get("port", daemon.default_port())
    url = daemon.public_url(host, port)

    pcfg = cfg.providers.get(provider)
    model_str = f"{provider} · {pcfg.model if pcfg else 'unknown'}"
    sess_disp = (sid[:18] + "…") if sid and len(sid) > 18 else (sid or (L("Mới", "New")))
    perm_color = yellow(perm) if perm != "full" else paint("31", "full (no confirm)")

    title = L("Nestor Agent v0.7.5 · Trò chuyện", "Nestor Agent v0.7.5 · Chat")
    sidebar = (
        banner_heading(model_str),
        banner_field(L("Phiên", "Session"), sess_disp),
    )
    enabled_mcp = sum(server.enabled for server in cfg.mcp_servers.values())
    details = [
        banner_heading(L("Tổng quan", "Overview")),
        banner_field(L("Quyền", "Access"), perm_color),
        banner_field(L("Nhà cung cấp đã cấu hình", "Configured providers"), str(len(cfg.providers))),
        banner_field(
            L("Máy chủ MCP đã bật / đã cấu hình", "MCP servers enabled / configured"),
            f"{enabled_mcp} / {len(cfg.mcp_servers)}",
        ),
        "",
        banner_heading("Gateway"),
        banner_field("Web UI", cyan(url)),
        banner_field(L("Trạng thái Gateway", "Gateway status"), "nestor status"),
        "",
        *available_skill_rows(cfg, max_categories=4),
        "",
        *document_processing_rows(cfg),
    ]
    tip = L("/help Lệnh · /skills Kỹ năng · Ctrl+D Thoát", "/help Commands · /skills Skills · Ctrl+D to exit")

    print_banner(
        title, [(line, "") for line in details], tip, sidebar=sidebar,
        sidebar_path=(L("Không gian làm việc", "Workspace"), str(cfg.workspace_path())),
        stars_row=0, wrap_sidebar_path=True,
    )


def print_onboard_banner(cfg: Config | None = None) -> None:
    """In dong chu NESTOR lon va khung huong dan khi chay `nestor onboard`."""
    from ..core import config as cfgmod
    from ..core.paths import ROOT
    from . import daemon

    if cfg is None:
        cfg = cfgmod.load()

    state = daemon.read_state()
    host = state.get("host", daemon.default_host())
    port = state.get("port", daemon.default_port())
    provider = cfg.providers.get(cfg.default_provider)
    model = f"{cfg.default_provider} · {provider.model}" if provider else cfg.default_provider
    on, off = L("bật", "on"), L("tắt", "off")
    details = [
        banner_heading(L("Cấu hình hiện tại", "Current configuration")),
        banner_field(L("Model mặc định", "Default model"), model),
        banner_field(L("Nhà cung cấp đã cấu hình", "Configured providers"), str(len(cfg.providers))),
        banner_field(L("Máy chủ MCP đã cấu hình", "Configured MCP servers"), str(len(cfg.mcp_servers))),
        *available_skill_rows(cfg, max_categories=0, compact=True),
        "",
        banner_heading(L("Gateway và truy cập", "Gateway and access")),
        banner_field("URL", cyan(daemon.public_url(host, port))),
        banner_field("Sandbox", cfg.agent.exec_sandbox),
        banner_field(L("Mật khẩu giao diện", "Interface password"),
                     L("đã đặt", "set") if cfg.auth.password_hash else L("chưa đặt", "not set")),
        banner_field("Telegram", on if cfg.channels.telegram.enabled else off),
        banner_field("Heartbeat", on if cfg.heartbeat.enabled else off),
        "",
        banner_heading(L("Bộ nhớ và tài liệu", "Memory and documents")),
        *document_processing_rows(cfg),
        banner_field(L("Tự lập chỉ mục", "Automatic indexing"), on if cfg.memory.auto_index else off),
    ]
    title = L("Nestor Agent v0.7.5 · Trình thiết lập", "Nestor Agent v0.7.5 · Setup Wizard")
    tip = L("↑/↓ Di chuyển · Enter Chọn · Space Đánh dấu", "↑/↓ Navigate · Enter Select · Space Toggle")
    print_banner(
        title, [(line, "") for line in details], tip,
        sidebar_path=(L("Dữ liệu", "Data"), str(ROOT)),
        stars_row=6,
    )


def print_open_banner(url: str, cfg: Config | None = None) -> None:
    """In dong chu NESTOR lon va khung thong tin khi chay `nestor open`."""
    if cfg is None:
        try:
            from ..core import config as cfgmod
            cfg = cfgmod.load()
        except Exception:
            cfg = None
    skills_count = len(_discover_skills(cfg))
    prov = (cfg.default_provider if cfg else "unknown") or "unknown"
    pcfg = cfg.providers.get(prov) if cfg else None
    model_str = f"{prov} · {pcfg.model if pcfg else 'unknown'}"
    if len(model_str) > 34:
        model_str = model_str[:31] + "…"

    title = L("  Nestor Agent v0.7.5 · Mở Giao diện Web (Web UI)", "  Nestor Agent v0.7.5 · Web UI")
    rows = [
        (f"  {L('Địa chỉ', 'URL')}:   {cyan(url)}", f"{L('Trạng thái', 'Status')}:  {green(L('Đang chạy', 'Running'))}  "),
        (f"  {L('Mô hình', 'Model')}: {model_str}", f"{L('Kỹ năng', 'Skills')}:   {green(f'{skills_count} loaded')}  "),
    ]
    tip = L("  Đang mở trình duyệt web...", "  Opening web browser...")

    print_banner(title, rows, tip)
