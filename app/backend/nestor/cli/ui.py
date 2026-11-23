"""Tien ich terminal dung chung: ngon ngu, mau, hoi dap. Chi dung thu vien chuan."""
import getpass
import os
import sys

_lang: str | None = None
COLOR = sys.stdout.isatty() and not os.environ.get("NO_COLOR")


def set_lang(lang: str) -> None:
    global _lang
    _lang = lang if lang in ("vi", "en") else None


def lang() -> str:
    """Prefer the CLI override, then NESTOR_LANG, and default to English."""
    global _lang
    if _lang:
        return _lang
    from ..core.env import getenv

    pick = getenv("LANG")
    if pick not in ("vi", "en"):
        pick = "en"
    _lang = pick
    return pick


def L(vi: str, en: str) -> str:
    """Chon cau theo ngon ngu hien tai: L('Đã xong', 'Done')."""
    return vi if lang() == "vi" else en


def paint(code: str, s: str) -> str:
    return f"\033[{code}m{s}\033[0m" if COLOR else s


def bold(s: str) -> str: return paint("1", s)
def dim(s: str) -> str: return paint("2", s)
def red(s: str) -> str: return paint("31", s)
def green(s: str) -> str: return paint("32", s)
def yellow(s: str) -> str: return paint("33", s)
def cyan(s: str) -> str: return paint("36", s)


def ok(msg: str) -> None: print(f"{green('✓')} {msg}")
def warn(msg: str) -> None: print(f"{yellow('!')} {msg}")
def bad(msg: str) -> None: print(f"{red('✗')} {msg}")
def info(msg: str) -> None: print(f"{cyan('•')} {msg}")
def err(msg: str) -> None: print(f"{red(L('Lỗi', 'Error'))}: {msg}", file=sys.stderr)


def interactive() -> bool:
    return sys.stdin.isatty() and sys.stdout.isatty()


def ask(prompt: str, default: str = "") -> str:
    """Hoi mot dong; Enter hoac het du lieu nhap (EOF) -> tra ve mac dinh."""
    suffix = f" [{default}]" if default else ""
    try:
        return input(f"{prompt}{suffix}: ").strip() or default
    except EOFError:
        print()
        return default


def ask_secret(prompt: str) -> str:
    """Nhap bi mat: an ky tu khi la terminal that; khi nhan qua pipe thi doc thang."""
    try:
        return (getpass.getpass(f"{prompt}: ") if sys.stdin.isatty() else input(f"{prompt}: ")).strip()
    except EOFError:
        return ""


def fmt_ts(ts: float | None) -> str:
    import time

    return time.strftime("%Y-%m-%d %H:%M", time.localtime(ts)) if ts else "—"


# ---------------------------------------------------------------------------
# Menu chon bang phim (mui ten len/xuong, Space, Enter) theo kieu cac CLI hien dai.
# Chi chay tren terminal POSIX that; khi nhan qua pipe/CI/Windows thi lui ve kieu go so.
# ---------------------------------------------------------------------------
import re
import shutil

_ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")
Option = "str | tuple[str, str]"  # nhan hoac (nhan, goi y)


def tty() -> bool:
    return os.name == "posix" and sys.stdin.isatty() and sys.stdout.isatty()


def _split(opt) -> tuple[str, str]:
    return (opt, "") if isinstance(opt, str) else (opt[0], opt[1])


def _fit(label: str, hint: str = "", reserve: int = 6) -> str:
    """Cat cho vua mot dong de menu khong bi tran dong (neu tran thi ve lai se hong)."""
    width = max(1, shutil.get_terminal_size((80, 24)).columns - reserve)
    plain = _ANSI.sub("", label)
    if len(plain) > width:
        label = plain[: width - 1] + "…"
        hint = ""
    elif hint and len(plain) + len(hint) + 2 > width:
        hint = hint[: max(0, width - len(plain) - 3)] + "…"
    return label + (f"  {dim(hint)}" if hint else "")


KEYS = {b"\x1b[A": "up", b"\x1b[B": "down", b"\x1b[C": "right", b"\x1b[D": "left", b"\x1bOA": "up", b"\x1bOB": "down", b"\x1bOC": "right", b"\x1bOD": "left",
        b"\x1b[H": "home", b"\x1b[F": "end", b"\x1bOH": "home", b"\x1bOF": "end", b"\x1b[1~": "home", b"\x1b[4~": "end"}


class _Raw:
    """Che do terminal 'cbreak' (doc tung phim, khong hien ky tu go) + an con tro; luon khoi phuc khi thoat."""

    def __enter__(self):
        import termios
        import tty as _tty

        self.fd = sys.stdin.fileno()
        self.old = termios.tcgetattr(self.fd)
        _tty.setcbreak(self.fd)
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()
        return self

    def __exit__(self, *exc):
        import termios

        termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old)
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()

    def key(self) -> str:
        import select

        b = os.read(self.fd, 1)
        if b == b"\x1b":  # phim dac biet gui chuoi thoat (mui ten...)
            buf = b
            while len(buf) < 6 and select.select([self.fd], [], [], 0.03)[0]:
                buf += os.read(self.fd, 1)
                if buf[-1:].isalpha() or buf.endswith(b"~"):
                    break
            return KEYS.get(buf, "esc" if buf == b"\x1b" else "other")
        if b in (b"\r", b"\n"):
            return "enter"
        if b == b" ":
            return "space"
        if b == b"\t":
            return "tab"
        if b in (b"", b"\x04"):
            raise EOFError
        if b == b"\x03":
            raise KeyboardInterrupt
        return b.decode("utf-8", "ignore").lower()


class _Screen:
    """Ve lai mot khoi dong tai cho (len N dong roi xoa xuong)."""

    def __init__(self) -> None:
        self.n = 0

    def draw(self, lines: list[str]) -> None:
        move_up = f"\033[{self.n}A" if self.n else ""
        surplus = max(0, self.n - len(lines))
        rendered = "".join(f"\033[2K{line}\n" for line in lines)
        clear_surplus = "\033[2K\n" * surplus + f"\033[{surplus}A" if surplus else ""
        sys.stdout.write(move_up + "\r" + rendered + clear_surplus)
        sys.stdout.flush()
        self.n = len(lines)


def select(prompt: str, options: list, default: int = 0, *, back: int | None = None) -> int:
    """Chon mot muc: mui ten len/xuong (hoac j/k), Home/End, phim so, Enter."""
    items = [_split(o) for o in options]
    idx, screen = max(0, min(default, len(items) - 1)), _Screen()
    help_line = dim("  " + L("↑/↓ di chuyển · Enter chọn", "↑/↓ move · Enter select"))
    if back is not None:
        help_line += dim(" · " + L("Esc quay lại", "Esc back"))
    with _Raw() as raw:
        while True:
            visible = max(1, shutil.get_terminal_size((80, 24)).lines - 5)
            start = min(max(0, idx - visible // 2), max(0, len(items) - visible))
            position = f" ({idx + 1}/{len(items)})" if len(items) > visible else ""
            lines = [f"{cyan('◆')} {bold(_fit(prompt, reserve=3 + len(position)))}{position}"]
            for i, (label, hint) in enumerate(items[start:start + visible], start):
                lines.append(f"{cyan('❯')} {cyan(bold(_fit(label, hint)))}" if i == idx else f"  {_fit(label, hint)}")
            screen.draw(lines + [_fit(help_line)])
            k = raw.key()
            if k in ("up", "k"):
                idx = (idx - 1) % len(items)
            elif k in ("down", "j", "tab"):
                idx = (idx + 1) % len(items)
            elif k == "home":
                idx = 0
            elif k == "end":
                idx = len(items) - 1
            elif k.isdigit() and 1 <= int(k) <= len(items):
                idx = int(k) - 1
            elif k == "esc" and back is not None:
                idx = back
                break
            elif k == "enter":
                break
        screen.draw([f"{green('◇')} {_fit(prompt, _ANSI.sub('', items[idx][0]))}"])
    return idx


def multiselect(prompt: str, options: list, defaults: set[int] | None = None) -> list[int]:
    """Chon nhieu muc: mui ten di chuyen, Space tick/bo tick, A chon het/bo het, Enter xac nhan."""
    items = [_split(o) for o in options]
    chosen = set(defaults or ())
    if not tty():
        return _multiselect_typed(prompt, items, chosen)
    idx, screen = 0, _Screen()
    help_line = dim("  " + L("↑/↓ di chuyển · Space chọn/bỏ · A tất cả · Enter xác nhận", "↑/↓ move · Space toggle · A all · Enter confirm"))
    with _Raw() as raw:
        while True:
            lines = [f"{cyan('◆')} {bold(prompt)}"]
            for i, (label, hint) in enumerate(items):
                box = green("◼") if i in chosen else dim("◻")
                text = _fit(label, hint, reserve=8)
                lines.append(f"{cyan('❯')} {box} {cyan(bold(text)) if i == idx else text}" if i == idx else f"  {box} {text}")
            screen.draw(lines + [help_line])
            k = raw.key()
            if k in ("up", "k"):
                idx = (idx - 1) % len(items)
            elif k in ("down", "j", "tab"):
                idx = (idx + 1) % len(items)
            elif k == "home":
                idx = 0
            elif k == "end":
                idx = len(items) - 1
            elif k == "space":
                chosen ^= {idx}
            elif k == "a":
                chosen = set() if len(chosen) == len(items) else set(range(len(items)))
            elif k == "enter":
                break
        picked = [_ANSI.sub("", items[i][0]) for i in sorted(chosen)]
        screen.draw([f"{green('◇')} {prompt}  {cyan(', '.join(picked) if picked else dim(L('(không chọn gì)', '(none)')))}"])
    return sorted(chosen)


def _multiselect_typed(prompt: str, items: list[tuple[str, str]], chosen: set[int]) -> list[int]:
    """Phien ban go so cho pipe/CI: '1,3' hoac Enter de lay mac dinh."""
    print(bold(prompt))
    for i, (label, _) in enumerate(items, 1):
        print(f"  {bold(str(i))}) [{'x' if i - 1 in chosen else ' '}] {label}")
    raw = ask(L("Nhập số cách nhau bằng dấu phẩy (Enter = mặc định, 0 = không chọn gì)", "Numbers separated by commas (Enter = defaults, 0 = none)"))
    if not raw:
        return sorted(chosen)
    if raw.strip() == "0":
        return []
    return sorted({int(x) - 1 for x in raw.replace(" ", "").split(",") if x.isdigit() and 1 <= int(x) <= len(items)})


def confirm(prompt: str, default: bool = True) -> bool:
    """Co/Khong: mui ten trai/phai (hoac y/n), Enter."""
    if not tty():
        hint = "Y/n" if default else "y/N"
        ans = ask(f"{prompt} ({hint})").lower()
        return default if not ans else ans.startswith(("y", "c"))  # y/yes; c = "co"
    yes, screen = default, _Screen()
    labels = (L("Có", "Yes"), L("Không", "No"))
    with _Raw() as raw:
        while True:
            a = f"{green('●')} {labels[0]}" if yes else f"{dim('○')} {dim(labels[0])}"
            b = f"{dim('○')} {dim(labels[1])}" if yes else f"{red('●')} {labels[1]}"
            screen.draw([f"{cyan('◆')} {bold(prompt)}  {a}  {dim('/')}  {b}"])
            k = raw.key()
            if k in ("left", "right", "up", "down", "tab", "h", "l", "space"):
                yes = not yes
            elif k in ("y", "c"):  # y/yes, c = "co"
                yes = True
            elif k == "n":
                yes = False
            elif k == "enter":
                break
        screen.draw([f"{green('◇')} {prompt}  {cyan(labels[0] if yes else labels[1])}"])
    return yes


def ask_yes_no(prompt: str, default: bool = True) -> bool:
    return confirm(prompt, default)


def choose(prompt: str, options: list, default: int = 0, *, back: int | None = None) -> int:
    """Menu chon mot muc; mui ten tren terminal that, danh so khi khong tuong tac."""
    if tty():
        return select(prompt, options, default, back=back)
    labels = [_split(o)[0] for o in options]
    for i, o in enumerate(labels, 1):
        print(f"  {bold(str(i))}) {o}")
    while True:
        try:
            raw = input(f"{prompt} [{default + 1}]: ").strip() or str(default + 1)
        except EOFError:
            print()
            return default if back is None else back
        if raw.isdigit() and 1 <= int(raw) <= len(labels):
            return int(raw) - 1
        print(red(L("  Hãy nhập một số trong danh sách.", "  Enter a number from the list.")))
        if not sys.stdin.isatty() and not raw:
            return default
