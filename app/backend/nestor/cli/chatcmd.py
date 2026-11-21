"""nestor chat (REPL) va nestor run (mot lan): chay agent ngay trong tien trinh, khong can server."""
from base64 import b64encode
from contextlib import contextmanager, redirect_stdout
from functools import lru_cache
from io import StringIO
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time

from ..services import api_run, chat_runner, sessions
from . import runtime
from .ui import L, ask_yes_no, bold, choose, cyan, dim, err, green, interactive, red, tty, yellow

KIND = {"exec": ("chạy lệnh shell", "run a shell command"), "mcp": ("gọi tool MCP", "call an MCP tool"), "file_read": ("đọc file ngoài workspace", "read a file outside the workspace"),
        "file_write": ("ghi file", "write a file"), "http_request": ("gửi yêu cầu HTTP thay đổi dữ liệu", "send a state-changing HTTP request")}
PERMS = ("default", "readonly", "guarded", "full", "plan")
EFFORTS = ("auto", "low", "medium", "high", "thinking")


_FOOTER_ROWS = 4
_FOOTER_COMMANDS = ("/model", "/perm", "/effort", "/open")


def _copy_selection(text: str, output) -> None:
    commands = []
    if os.environ.get("WAYLAND_DISPLAY"):
        commands.append(["wl-copy"])
    if os.environ.get("DISPLAY"):
        commands.append(["xclip", "-selection", "clipboard"])
        commands.append(["xsel", "--clipboard", "--input"])
    for command in commands:
        if shutil.which(command[0]):
            try:
                subprocess.run(command, input=text.encode("utf-8"), stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL, check=True, timeout=2)
                return
            except (OSError, subprocess.SubprocessError):
                continue
    encoded = b64encode(text.encode("utf-8")).decode("ascii")
    output.write_raw(f"\x1b]52;c;{encoded}\x07")
    output.flush()


def _user_message_text(text: str) -> str:
    visible = re.sub(r"[\x00-\x08\x0b-\x1f\x7f-\x9f]", "�", text)
    return cyan(visible.replace("\n", "\n  "))


def _chat_markdown(text: str) -> str:
    from rich.console import Console
    from rich.markdown import Markdown
    from .ui import COLOR

    output = StringIO()
    columns = shutil.get_terminal_size((80, 24)).columns
    console = Console(file=output, width=max(1, columns - 1), force_terminal=COLOR, highlight=False, legacy_windows=False)
    console.print(Markdown(text, hyperlinks=False))
    return re.sub(r" +((?:\x1b\[[0-9;]*m)*)(?=\n|$)", r"\1", output.getvalue()).strip("\n")


class _ChatTranscript:
    def __init__(self, terminal):
        self.terminal = terminal
        self.buffer = StringIO()

    def write(self, text):
        self.buffer.write(text)
        return self.terminal.write(text)

    def __getattr__(self, name):
        return getattr(self.terminal, name)

    def text(self):
        # Retain SGR styling, but discard cursor commands and other control characters.
        return re.sub(
            r"(\x1b\[[0-9;]*m)|\x1b\[[0-?]*[ -/]*[@-~]|[\x00-\x08\x0b-\x1f\x7f-\x9f]",
            lambda match: match[1] or "",
            self.buffer.getvalue(),
        )

    def load(self, sid):
        self.buffer = StringIO()
        if sid:
            for msg in sessions.messages(sid):
                if msg["role"] in ("user", "assistant") and msg.get("content"):
                    content = msg["content"]
                    if msg["role"] == "user":
                        content = cyan("> ") + _user_message_text(content)
                    else:
                        content = _chat_markdown(content)
                    self.buffer.write(f"{content}\n\n")


def _chat_status(cfg, st, columns: int, selecting: bool = False, active_field: int | None = None) -> str:
    from prompt_toolkit.utils import get_cwidth

    provider = cfg.providers[st["provider"]]
    model = provider.model or provider.type
    session = st["sid"] or L("Mới", "New")
    controls = r"[\x00-\x1f\x7f-\x9f]"
    fields = [re.sub(controls, " ", field) for field in (
        f"{st['provider']} / {model}",
        f"{L('Quyền', 'Perm')} {st['perm']}",
        f"{L('Suy nghĩ', 'Effort')} {st['effort']}",
        f"{L('Phiên', 'Session')} {session}",
    )]
    left = "  " + fields[0]
    if selecting:
        left += "  ·  " + L("F2: Bật cuộn chuột", "F2: Enable mouse scrolling")
    separator = "  ·  "
    right = separator.join(fields[1:])
    gap = columns - get_cwidth(left) - get_cwidth(right)
    prefix = left + (separator if gap < 4 else " " * (gap - 2))
    status = _fit_terminal_line(prefix + right, columns)
    if active_field is None:
        return status
    field = fields[active_field]
    start = 2 if active_field == 0 else len(prefix) + sum(len(item) + len(separator) for item in fields[1:active_field])
    stop = start + len(field)
    if stop > len(status) or (status.endswith("…") and stop == len(status)):
        return f"  \033[1;7m{_fit_terminal_line(field, max(1, columns - 2))}\033[0m"
    return f"{status[:start]}\033[1;7m{status[start:stop]}\033[0m{dim(status[stop:])}"


def _fit_terminal_line(text: str, columns: int) -> str:
    from prompt_toolkit.utils import get_cwidth

    if get_cwidth(text) <= columns:
        return text
    width = 0
    for index, char in enumerate(text):
        width += get_cwidth(char)
        if width >= columns:
            return text[:index] + "…"
    return text


@contextmanager
def _busy_chat_footer(cfg, st, prompt: str, enabled: bool, terminal=None):
    if not enabled or not tty() or os.environ.get("TERM") == "dumb":
        yield
        return
    cols, rows = shutil.get_terminal_size((80, 24))
    if rows <= _FOOTER_ROWS + 1 or cols < 8:
        yield
        return

    import termios

    terminal = terminal if terminal is not None else sys.stdout
    fd = sys.stdin.fileno()
    previous = termios.tcgetattr(fd)
    quiet = previous.copy()
    quiet[3] &= ~termios.ECHO

    # Make room below the transcript cursor, scrolling only if already near the bottom.
    # DECSTBM then keeps streaming output inside the rows above the footer.
    bottom = rows - _FOOTER_ROWS
    border = f"\033[90m{'─' * (cols - 1)}\033[0m"
    waiting = _fit_terminal_line(L("Đang trả lời…", "Responding…"), cols - 3)
    status = dim(_chat_status(cfg, st, cols - 1))
    footer = (border, prompt + dim(waiting), border, status)
    try:
        termios.tcsetattr(fd, termios.TCSANOW, quiet)
        terminal.write(
            "\n" * _FOOTER_ROWS + f"\033[{_FOOTER_ROWS}A\0337\033[1;{bottom}r"
            + "".join(f"\033[{bottom + n};1H\033[2K{line}" for n, line in enumerate(footer, 1))
            + "\0338"
        )
        terminal.flush()
        yield
    finally:
        try:
            terminal.write("\0337\033[r\0338\033[J")
            terminal.flush()
        finally:
            termios.tcsetattr(fd, termios.TCSANOW, previous)


class ThinkingSpinner:
    """Hieu ung animation spinner khi Nestor / model dang suy nghi hoac goi tool."""
    FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    def __init__(self, message: str = "Nestor đang suy nghĩ...", terminal=None):
        self.message = message
        self._stop = threading.Event()
        self._active = False
        self._thread: threading.Thread | None = None
        self._t0 = time.time()
        self._terminal = terminal if terminal is not None else sys.stdout
        self._isatty = self._terminal.isatty()
        self._lock = threading.Lock()

    def start(self, message: str | None = None) -> None:
        if not self._isatty:
            return
        if message:
            self.message = message
        if self._active:
            return
        self._stop.clear()
        self._active = True
        self._t0 = time.time()
        self._thread = threading.Thread(target=self._spin, daemon=True)
        self._thread.start()

    def set_message(self, message: str) -> None:
        self.message = message

    def _spin(self) -> None:
        idx = 0
        while not self._stop.is_set():
            frame = self.FRAMES[idx % len(self.FRAMES)]
            elapsed = time.time() - self._t0
            sec = f" ({elapsed:.1f}s)" if elapsed >= 1.0 else ""
            available = max(1, shutil.get_terminal_size((80, 24)).columns - len(sec) - 6)
            message = _fit_terminal_line(self.message, available)
            line = f"\r  {cyan(frame)} {dim(message)}{dim(sec)} \033[K"
            with self._lock:
                if self._stop.is_set():
                    break
                try:
                    self._terminal.write(line)
                    self._terminal.flush()
                except Exception:
                    pass
            idx += 1
            time.sleep(0.08)

    def stop(self, clear: bool = True) -> None:
        if not self._active:
            return
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=0.3)
        self._active = False
        with self._lock:
            if clear and self._isatty:
                try:
                    self._terminal.write("\r\033[K")
                    self._terminal.flush()
                except Exception:
                    pass


def _trace(ev: dict) -> str | None:
    if ev["type"] == "tool":
        a = ev["args"]
        summary = a.get("command") if ev["name"] == "exec" else (a.get("path") or a.get("url") or a.get("query") or json.dumps(a, ensure_ascii=False))
        return f"⚙ {ev['name']} {str(summary)[:140]}"
    if ev["type"] == "tool_result":
        first = (ev["result"].strip().splitlines() or [""])[0][:120]
        return f"  {'→' if ev['ok'] else '✗'} {first}  ({ev.get('duration_ms', 0)}ms)"
    return None


def consume(events, *, live: bool, verbose: bool, ask: bool, deadline: float | None = None,
            spinner: ThinkingSpinner | None = None, transcript: _ChatTranscript | None = None) -> dict:
    """Doc su kien tu stream_chat. live=True: in chu khi model dang sinh; ask=True: hoi y/N khi can phe duyet."""
    out = {"session": None, "output": "", "error": None, "timed_out": False, "provider": None, "usage": {"prompt": 0, "completion": 0}}
    streamed = False
    answer_streamed = False
    in_thinking = False
    terminal = transcript.terminal if transcript is not None else sys.stdout
    try:
        for ev in events:
            t = ev["type"]
            if t == "session":
                out["session"] = ev["id"]
            elif t == "status":
                msg = ev.get("text") or ev.get("message") or ""
                if msg and spinner:
                    spinner.set_message(msg)
            elif live and transcript is not None and t in ("thinking", "tool", "tool_result", "notice"):
                if spinner and not answer_streamed:
                    if t == "thinking":
                        spinner.start(L("Nestor đang suy nghĩ…", "Nestor is thinking…"))
                    elif t == "tool":
                        spinner.start(L(f"Đang thực hiện {ev['name']}…", f"Running {ev['name']}…"))
                    elif t == "notice":
                        message = " ".join(ev["message"].split())
                        spinner.start(message)
            elif t == "thinking":
                if spinner:
                    spinner.stop(clear=True)
                if live:
                    if not in_thinking:
                        in_thinking = True
                        sys.stdout.write(dim("💭 "))
                    sys.stdout.write(dim(ev["text"]))
                    sys.stdout.flush()
                    streamed = True
                elif verbose:
                    print(dim(ev["text"]), end="", file=sys.stderr, flush=True)
            elif t == "delta" and live:
                if spinner:
                    spinner.stop(clear=True)
                if in_thinking:
                    in_thinking = False
                    sys.stdout.write("\n\n")
                    sys.stdout.flush()
                terminal.write(ev["text"])
                terminal.flush()
                streamed = True
                answer_streamed = True
            elif t == "assistant":
                if spinner:
                    spinner.stop(clear=True)
                if in_thinking:
                    in_thinking = False
                    sys.stdout.write("\n\n")
                    sys.stdout.flush()
                out["output"], out["provider"] = ev["content"], ev["provider"]
                out["usage"] = {k: out["usage"][k] + ev["usage"][k] for k in out["usage"]}
                if live and transcript is not None and answer_streamed:
                    transcript.terminal.write("\n")
                    transcript.terminal.flush()
                    if ev["content"]:
                        transcript.buffer.write(_chat_markdown(ev["content"]) + "\n")
                elif live and transcript is not None and ev["content"]:
                    print(_chat_markdown(ev["content"]), flush=True)
                elif live and streamed:
                    sys.stdout.write("\n")
                    sys.stdout.flush()
                elif live and ev["content"]:
                    sys.stdout.write(ev["content"] + "\n")
                    sys.stdout.flush()
                streamed = False
                answer_streamed = False
            elif t in ("tool", "tool_result") and (verbose or live):
                if spinner:
                    spinner.stop(clear=True)
                if in_thinking:
                    in_thinking = False
                    sys.stdout.write("\n\n")
                    sys.stdout.flush()
                line = _trace(ev)
                if line:
                    print(dim(line), file=sys.stdout if live else sys.stderr, flush=True)
                if spinner and t == "tool":
                    spinner.start(L(f"Đang thực hiện {ev.get('name', 'tool')}...", f"Running {ev.get('name', 'tool')}..."))
            elif t == "approval":
                if spinner:
                    spinner.stop(clear=True)
                if in_thinking:
                    in_thinking = False
                    sys.stdout.write("\n\n")
                    sys.stdout.flush()
                label = KIND.get(ev["kind"], (ev["kind"], ev["kind"]))
                with redirect_stdout(terminal):
                    print(f"\n{yellow('⚠')} {L('Agent muốn', 'The agent wants to')} {bold(L(label[0], label[1]))}:\n  {ev['detail'][:500]}", file=sys.stderr if not live else terminal)
                    allowed = ask and ask_yes_no(L("Cho phép?", "Allow?"), False)
                chat_runner.resolve_approval(ev["id"], allowed)
            elif t == "notice" and (verbose or live):
                print(dim(f"· {ev['message']}"), file=sys.stderr if not live else sys.stdout)
            elif t == "error":
                if spinner:
                    spinner.stop(clear=True)
                if in_thinking:
                    in_thinking = False
                    sys.stdout.write("\n\n")
                    sys.stdout.flush()
                out["error"] = ev["message"]
            if deadline and time.time() > deadline:
                out["timed_out"], out["error"] = True, out["error"] or L("hết thời gian chờ", "timed out")
                break
    finally:
        if spinner:
            spinner.stop(clear=True)
        events.close()
    return out


def _read_prompt(p: str) -> str:
    return sys.stdin.read().strip() if p == "-" else p


def run(args) -> int:
    prompt = _read_prompt(args.prompt)
    if not prompt:
        err(L("Thiếu nội dung yêu cầu.", "Missing prompt."))
        return 2
    runtime.bootstrap(with_mcp=True)
    tools = [t.strip() for t in args.tools.split(",")] if args.tools else None
    effort = None if args.effort == "auto" else args.effort
    if args.ask and not interactive():
        err(L("--ask cần terminal tương tác.", "--ask needs an interactive terminal."))
        return 2
    try:
        approver = None if args.ask else api_run.make_approver(args.exec_policy, args.allow or [], True)
    except api_run.PolicyError as e:
        err(str(e))
        return 2
    if args.json:
        res = api_run.run_once(prompt, session=args.session, provider=args.provider, approver=approver or (lambda k, d: False), only_tools=tools,
                               timeout=args.timeout, permission=args.permission, effort=effort, source="cli")
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return 1 if res["error"] else 0
    events = chat_runner.stream_chat(args.session, prompt, args.provider, approver_override=approver, source="cli", only_tools=tools, permission=args.permission, effort=effort)
    spinner = ThinkingSpinner(L("Nestor đang xử lý...", "Nestor is working..."))
    spinner.start()
    try:
        res = consume(events, live=True, verbose=args.verbose, ask=args.ask, deadline=time.time() + args.timeout, spinner=spinner)
    finally:
        spinner.stop(clear=True)
    if res["error"]:
        err(res["error"])
        return 1
    return 0


HELP = {
    "/help": ("Hiện trợ giúp", "Show help"), "/new": ("Bắt đầu hội thoại mới", "Start a new conversation"), "/sessions": ("Liệt kê hội thoại gần đây", "List recent conversations"),
    "/open <id>": ("Mở lại một hội thoại", "Reopen a conversation"), "/model [name]": ("Xem & đổi model/provider", "List & switch model/provider"), "/perm <mode>": ("default | readonly | guarded | full", "default | readonly | guarded | full"),
    "/effort <level>": ("auto | low | medium | high | thinking", "auto | low | medium | high | thinking"), "/skills": ("Liệt kê skill", "List skills"), "/files": ("Liệt kê file của phiên", "List the conversation's files"),
    "/status": ("Model, quyền, mức suy nghĩ, usage phiên", "Model, permissions, effort, session usage"),
    "/retry": ("Gửi lại tin nhắn cuối", "Resend the last message"),
    "/undo": ("Hoàn tác file của lượt gần nhất (giữ nguyên hội thoại)", "Undo files from the last turn (keeps the conversation)"),
    "/rewind [n]": ("Lùi lại n tin của bạn rồi sửa & gửi lại", "Rewind n of your messages, then edit & resend"),
    "/compress": ("Nén bớt hội thoại cũ (tóm tắt) để đỡ tốn ngữ cảnh", "Summarize older turns to save context"),
    "/diff": ("Xem git diff của dự án", "Show the project's git diff"),
    "/exit": ("Thoát (hoặc Ctrl+D)", "Quit (or Ctrl+D)"),
}


def _make_reader(cfg, st, transcript=None):
    """Trả về hàm đọc dòng có giao diện hộp nhập dưới cùng phong cách Claude Code (kèm autocomplete lệnh)."""
    try:
        from prompt_toolkit import PromptSession
        from prompt_toolkit.application import get_app
        from prompt_toolkit.completion import Completer, Completion
        from prompt_toolkit.filters import Always, Condition
        from prompt_toolkit.formatted_text import ANSI
        from prompt_toolkit.formatted_text.utils import split_lines
        from prompt_toolkit.history import InMemoryHistory
        from prompt_toolkit.key_binding import KeyBindings
        from prompt_toolkit.layout.containers import FloatContainer, Window
        from prompt_toolkit.layout.controls import FormattedTextControl, UIContent, UIControl
        from prompt_toolkit.layout.dimension import Dimension
        from prompt_toolkit.mouse_events import MouseButton, MouseEventType
        from prompt_toolkit.styles import Style
        from prompt_toolkit.utils import get_cwidth
    except ImportError:
        return None
    if not (sys.stdin.isatty() and sys.stdout.isatty()):
        return None

    keys = KeyBindings()
    transcript_text = ""
    mouse_enabled = transcript is not None
    footer_field = None
    footer_command = None
    continuation = False

    @Condition
    def footer_active():
        return footer_field is not None and not session.default_buffer.text

    @Condition
    def empty_prompt():
        buffer = session.default_buffer
        return not continuation and not buffer.text and buffer.complete_state is None

    @keys.add("down", filter=empty_prompt, eager=True)
    @keys.add("right", filter=footer_active, eager=True)
    @keys.add("left", filter=footer_active, eager=True)
    def move_footer(event):
        nonlocal footer_field
        if footer_field is None:
            footer_field = 0
        else:
            direction = -1 if event.key_sequence[0].key == "left" else 1
            footer_field = (footer_field + direction) % len(_FOOTER_COMMANDS)

    @keys.add("up", filter=footer_active, eager=True)
    @keys.add("escape", filter=footer_active, eager=True)
    def leave_footer(event):
        nonlocal footer_field
        footer_field = None

    @keys.add("enter", filter=footer_active, eager=True)
    def open_footer_field(event):
        nonlocal footer_command
        footer_command = _FOOTER_COMMANDS[footer_field]
        event.app.exit(result=footer_command)

    if transcript is not None:
        @keys.add("f2")
        def toggle_mouse(event):
            nonlocal mouse_enabled
            mouse_enabled = not mouse_enabled

    @lru_cache(maxsize=1)
    def wrapped_lines(width):
        lines = []
        for fragments in split_lines(ANSI(transcript_text).__pt_formatted_text__()):
            row = []
            used = 0
            for style, text in fragments:
                for char in text:
                    value = " " * (4 - used % 4) if char == "\t" else char
                    cells = get_cwidth(value)
                    if used and used + cells > width:
                        lines.append((row, ""))
                        row, used = [], 0
                    row.extend((style, char) for char in value)
                    used += cells
            lines.append((row, "\n"))
        return lines

    class TranscriptControl(UIControl):
        offset = 0
        max_offset = 0
        start = 0
        width = 0
        anchor = None
        endpoint = None
        dragging = False

        def scroll(self, lines):
            self.offset = max(0, min(self.max_offset, self.offset + lines))

        def create_content(self, width, height):
            if self.width != width:
                self.clear_selection()
                self.width = width
            lines = wrapped_lines(max(1, width))
            self.max_offset = max(0, len(lines) - height)
            self.offset = min(self.offset, self.max_offset)
            self.start = self.max_offset - self.offset
            visible = lines[self.start:self.start + height]

            def get_line(index):
                row, _ = visible[index]
                # Give empty lines a character position for mouse-event mapping.
                end = [("", " ")]
                if self.endpoint is None or self.anchor == self.endpoint:
                    return row + end
                first, last = sorted((self.anchor, self.endpoint))
                y = self.start + index
                if not first[0] <= y <= last[0]:
                    return row + end
                left = first[1] if y == first[0] else 0
                right = last[1] + 1 if y == last[0] else len(row)
                selected = [(style + " reverse", char) for style, char in row[left:right]]
                return row[:left] + selected + row[right:] + end

            return UIContent(get_line=get_line, line_count=len(visible), show_cursor=False)

        def clear_selection(self):
            self.anchor = self.endpoint = None
            self.dragging = False

        def selected_text(self):
            first, last = sorted((self.anchor, self.endpoint))
            lines = wrapped_lines(max(1, self.width))
            chunks = []
            for y in range(first[0], last[0] + 1):
                row, separator = lines[y]
                left = first[1] if y == first[0] else 0
                right = last[1] + 1 if y == last[0] else len(row)
                chunks.append("".join(char for _, char in row[left:right]))
                if y < last[0]:
                    chunks.append(separator)
            return "".join(chunks)

        def mouse_handler(self, event):
            if event.event_type == MouseEventType.SCROLL_UP:
                self.scroll(3)
            elif event.event_type == MouseEventType.SCROLL_DOWN:
                self.scroll(-3)
            elif event.event_type == MouseEventType.MOUSE_DOWN and event.button == MouseButton.LEFT:
                self.anchor = self.endpoint = (self.start + event.position.y, event.position.x)
                self.dragging = True
            elif self.dragging and event.event_type in (MouseEventType.MOUSE_MOVE, MouseEventType.MOUSE_UP):
                if event.event_type == MouseEventType.MOUSE_MOVE and event.button != MouseButton.LEFT:
                    self.dragging = False
                    return
                self.endpoint = (self.start + event.position.y, event.position.x)
                if event.event_type == MouseEventType.MOUSE_UP:
                    self.dragging = False
                    if self.endpoint != self.anchor and (text := self.selected_text()):
                        _copy_selection(text, get_app().output)
            else:
                return NotImplemented

    transcript_control = TranscriptControl()
    transcript_window = Window(transcript_control)
    if transcript is not None:
        @keys.add("pageup", eager=True)
        @keys.add("pagedown", eager=True)
        def scroll_page(event):
            info = transcript_window.render_info
            page = max(1, info.window_height - 1) if info else 1
            transcript_control.scroll(page if event.key_sequence[0].key == "pageup" else -page)

    class SlashCompleter(Completer):
        def get_completions(self, document, complete_event):
            text = document.text_before_cursor
            if not text.startswith("/") or "\n" in text:
                return
            if " " not in text:
                for k, (vi, en) in HELP.items():
                    name = k.split(" ")[0]
                    if name.startswith(text):
                        yield Completion(name, start_position=-len(text), display=k, display_meta=L(vi, en))
                return
            cmd, _, partial = text.partition(" ")
            if cmd == "/model":
                opts = [(n, (cfg.providers[n].model or cfg.providers[n].type) + (" ●" if n == st.get("provider") else "")) for n in cfg.providers]
            elif cmd == "/perm":
                opts = [(n, "") for n in PERMS]
            elif cmd == "/effort":
                opts = [(n, "") for n in EFFORTS]
            elif cmd == "/open":
                opts = [(x["id"], x["title"][:40]) for x in sessions.list_all(10)]
            else:
                return
            for name, meta in opts:
                if name.startswith(partial):
                    yield Completion(name, start_position=-len(partial), display_meta=meta)

    class ChatPromptSession(PromptSession):
        def _create_layout(self):
            layout = super()._create_layout()
            body = layout.container
            prompt_container = body.children[0]
            input_container = getattr(prompt_container, "alternative_content", prompt_container)
            completion_floats = [item for item in input_container.floats if item.ycursor]
            input_container.floats = [item for item in input_container.floats if not item.ycursor]
            layout.current_window.dont_extend_height = Always()

            def menu_height():
                state = self.default_buffer.complete_state
                available = max(0, self.app.output.get_size().rows - _FOOTER_ROWS - 1)
                return min(len(state.completions), 8, available) if state else 0

            def border_text():
                cols = self.app.output.get_size().columns
                return ANSI(f"\033[90m{'─' * cols}\033[0m")

            def border():
                return Window(FormattedTextControl(border_text), height=1)

            def status_text():
                cols = self.app.output.get_size().columns
                field = footer_field if footer_active() else None
                return ANSI(dim(_chat_status(cfg, st, cols - 1, selecting=transcript is not None and not mouse_enabled, active_field=field)))

            body.children.insert(0, Window(height=lambda: Dimension.exact(menu_height())))
            body.children.insert(1, border())
            body.children.extend([
                border(),
                Window(FormattedTextControl(status_text), height=1),
            ])
            if transcript is not None:
                body.children.insert(0, transcript_window)
            # Give completions room above the cursor when the prompt is at the bottom.
            for menu in completion_floats:
                menu.ycursor = False
                menu.bottom = _FOOTER_ROWS
                menu.height = menu_height
            layout.container = FloatContainer(body, completion_floats)
            return layout

        def _create_application(self, editing_mode, erase_when_done):
            app = super()._create_application(editing_mode, erase_when_done)
            if transcript is not None:
                app.full_screen = app.renderer.full_screen = True
            return app

    session = ChatPromptSession(
        completer=SlashCompleter(),
        complete_while_typing=True,
        history=InMemoryHistory(),
        reserve_space_for_menu=0,
        erase_when_done=True,
        key_bindings=keys,
        mouse_support=Condition(lambda: mouse_enabled),
        style=Style.from_dict({
            "completion-menu": "bg:#20252c",
            "completion-menu.completion": "bg:#20252c fg:#bce9f1",
            "completion-menu.meta.completion": "bg:#20252c fg:#aeb8c5",
            "completion-menu.completion.current": "bg:#294650 fg:#8eeeff bold noreverse",
            "completion-menu.meta.completion.current": "bg:#294650 fg:#e3edf4 noreverse",
            "completion-menu scrollbar.background": "bg:#20252c",
            "completion-menu scrollbar.button": "bg:#526676",
        }),
    )

    def read(prompt: str) -> str:
        nonlocal transcript_text, footer_field, footer_command, continuation
        footer_field = footer_command = None
        continuation = False
        if transcript is not None:
            transcript_text = transcript.text()
            wrapped_lines.cache_clear()
            transcript_control.offset = 0
            transcript_control.clear_selection()
        line = session.prompt(ANSI(prompt)).strip()
        if footer_command is not None:
            return footer_command
        while line.endswith("\\"):
            continuation = True
            line = line[:-1] + "\n" + session.prompt(ANSI(dim("  … "))).rstrip()
        if line:
            print(prompt + _user_message_text(line), flush=True)
        return line

    return read


def chat(args) -> int:
    import logging
    logging.getLogger("mcp").setLevel(logging.CRITICAL)
    cfg = runtime.bootstrap(with_mcp=True)
    try:
        import readline  # noqa: F401 - bat lich su phim mui ten cho input()
    except ImportError:
        pass
    st = {"sid": args.session, "provider": args.provider or cfg.default_provider, "perm": args.permission, "effort": args.effort}
    if st["provider"] not in cfg.providers:
        err(L(f"Không có provider '{st['provider']}'. Có: {', '.join(cfg.providers)}", f"No provider '{st['provider']}'. Available: {', '.join(cfg.providers)}"))
        return 2
    from .banner import print_chat_banner
    transcript = _ChatTranscript(sys.stdout) if tty() and os.environ.get("TERM") != "dumb" else None
    reader = _make_reader(cfg, st, transcript)
    if reader is not None and transcript is not None:
        with redirect_stdout(transcript):
            print_chat_banner(cfg, st["provider"], st["perm"], st["sid"])
            if st["sid"]:
                transcript.load(st["sid"])
            return _chat_loop(cfg, st, reader, transcript)
    print_chat_banner(cfg, st["provider"], st["perm"], st["sid"])
    return _chat_loop(cfg, st, reader)


def _chat_loop(cfg, st, reader, transcript=None) -> int:
    terminal = transcript.terminal if transcript is not None else sys.stdout

    def choose_in_terminal(title, options, default):
        with redirect_stdout(terminal):
            return choose(title, options, default)

    prompt_str = f"{cyan('>')} "
    while True:
        try:
            if reader:
                line = reader(prompt_str)
            else:
                cols = shutil.get_terminal_size((80, 24)).columns
                border = "─" * cols
                if sys.stdout.isatty():
                    print(f"\033[90m{border}\033[0m")
                print(prompt_str, end="", flush=True)
                line = input().strip()
                if sys.stdout.isatty():
                    print(f"\033[90m{border}\033[0m")
                while line.endswith("\\"):
                    print(dim("  … "), end="", flush=True)
                    line = line[:-1] + "\n" + input().rstrip()
        except EOFError:
            print()
            return 0
        except KeyboardInterrupt:
            print()
            continue
        if not line:
            continue
        if line.startswith("/"):
            resend = False
            cmd, _, rest = line.partition(" ")
            rest = rest.strip()
            if cmd in ("/exit", "/quit", "/q"):
                return 0
            if cmd == "/help":
                for k, (vi, en) in HELP.items():
                    print(f"  {bold(k.ljust(14))}{L(vi, en)}")
                if transcript is not None:
                    print(f"  {bold('F2'.ljust(14))}{L('Chuyển giữa cuộn chuột và chọn văn bản', 'Toggle between mouse scrolling and text selection')}")
            elif cmd == "/new":
                st["sid"] = None
                if transcript is not None:
                    transcript.load(None)
                print(dim(L("Đã bắt đầu hội thoại mới.", "Started a new conversation.")))
            elif cmd == "/sessions":
                for s in sessions.list_all(10):
                    print(f"  {s['id']}  {s['title'][:50]}  {dim(time.strftime('%m-%d %H:%M', time.localtime(s['updated'])))}")
            elif cmd == "/open":
                if not rest and reader is not None:
                    recent = sessions.list_all(10)
                    if not recent:
                        print(dim(L("Chưa có hội thoại để mở.", "No conversations to open.")))
                        continue
                    options = [(s["title"][:50], s["id"]) for s in recent]
                    default = next((i for i, s in enumerate(recent) if s["id"] == st["sid"]), 0)
                    try:
                        rest = recent[choose_in_terminal(L("Chọn phiên", "Pick a session"), options, default)]["id"]
                    except (EOFError, KeyboardInterrupt):
                        print()
                        continue
                if not rest or not sessions.get(rest):
                    print(red(L("Không tìm thấy hội thoại.", "Conversation not found.")))
                    continue
                st["sid"] = rest
                if transcript is not None:
                    transcript.load(rest)
                print(dim(L(f"Đã mở {rest} ({len(sessions.messages(rest))} tin).", f"Opened {rest} ({len(sessions.messages(rest))} messages).")))
            elif cmd == "/model":
                names = list(cfg.providers)
                if not rest:
                    opts = [(f"{'●' if n == st['provider'] else ' '} {n}", cfg.providers[n].model or cfg.providers[n].type) for n in names]
                    try:
                        rest = names[choose_in_terminal(L("Chọn model", "Pick a model"), opts, names.index(st["provider"]) if st["provider"] in names else 0)]
                    except (EOFError, KeyboardInterrupt):
                        print()
                        continue
                if rest.isdigit() and 1 <= int(rest) <= len(names):
                    rest = names[int(rest) - 1]
                if rest in cfg.providers:
                    st["provider"] = rest
                    print(dim(L(f"Đã chuyển sang {rest} ({cfg.providers[rest].model or cfg.providers[rest].type}).", f"Switched to {rest} ({cfg.providers[rest].model or cfg.providers[rest].type}).")))
                else:
                    print(red(L(f"Không có provider '{rest}'. Gõ /model để xem danh sách.", f"No provider '{rest}'. Type /model to list.")))
            elif cmd in ("/perm", "/effort") and not rest and interactive():
                key, vals = ("perm", PERMS) if cmd == "/perm" else ("effort", EFFORTS)
                try:
                    st[key] = vals[choose_in_terminal(L("Chọn quyền", "Pick permissions") if key == "perm" else L("Chọn mức suy nghĩ", "Pick effort"), [("● " if v == st[key] else "  ") + v for v in vals], vals.index(st[key]) if st[key] in vals else 0)]
                except (EOFError, KeyboardInterrupt):
                    print()
                    continue
                print(dim(f"{key}: {st[key]}"))
            elif cmd == "/perm" and rest in PERMS:
                st["perm"] = rest
                print(dim(f"{L('Quyền', 'Permissions')}: {rest}") + (red(L("  (không hỏi xác nhận!)", "  (no confirmations!)")) if rest == "full" else ""))
            elif cmd == "/effort" and rest in EFFORTS:
                st["effort"] = rest
            elif cmd == "/skills":
                from ..services import skills as skillmod

                for s in skillmod.discover(cfg).values():
                    print(f"  {s.name}  {dim(s.description[:70])}")
            elif cmd == "/files" and st["sid"]:
                from ..services import workfiles

                for f in workfiles.tree(workfiles.session_dir(cfg, st["sid"])):
                    print(f"  {f['path']}{'/' if f['dir'] else ''}")
            elif cmd == "/status":
                pc = cfg.providers.get(st["provider"])
                print(f"  {L('Model', 'Model')}: {bold(st['provider'])} ({dim(pc.model or pc.type if pc else '?')})")
                print(f"  {L('Quyền', 'Permissions')}: {st['perm']}" + (red(L(' (full)', ' (full)')) if st["perm"] == "full" else ""))
                print(f"  {L('Mức suy nghĩ', 'Effort')}: {st['effort']}")
                print(f"  {L('Phiên', 'Session')}: {st['sid'] or dim(L('(chưa có)', '(none yet)'))}")
                if st["sid"]:
                    msgs = sessions.messages(st["sid"])
                    chars = sum(len(m.get("content", "")) for m in msgs)
                    print(f"  {L('Tin nhắn', 'Messages')}: {len(msgs)}  ·  ~{chars // 4} tokens {dim(L('(ước lượng)', '(estimate)'))}")
            elif cmd == "/retry":
                if not st["sid"]:
                    print(red(L("Chưa có hội thoại để gửi lại.", "No conversation to retry yet.")))
                    continue
                msgs = sessions.messages(st["sid"])
                last_user = next((m["content"] for m in reversed(msgs) if m["role"] == "user"), None)
                if not last_user:
                    print(red(L("Không tìm thấy tin nhắn trước đó.", "No previous message found.")))
                    continue
                line, resend = last_user, True
            elif cmd == "/undo":
                from ..services import checkpoints

                if not st["sid"]:
                    continue
                restored = checkpoints.undo(st["sid"])
                print(dim(L(f"Đã hoàn tác {len(restored)} file." if restored else "Không có gì để hoàn tác.",
                             f"Restored {len(restored)} file(s)." if restored else "Nothing to undo.")))
            elif cmd.startswith("/rewind"):
                if not st["sid"]:
                    continue
                n = int(rest) if rest.isdigit() else 1
                msgs = sessions.messages(st["sid"])
                user_idx = [i for i, m in enumerate(msgs) if m["role"] == "user"]
                if len(user_idx) < n:
                    print(red(L("Không đủ tin nhắn để lùi lại.", "Not enough messages to rewind.")))
                    continue
                cut = user_idx[-n]
                prior_text = msgs[cut]["content"]
                sessions.truncate_from(st["sid"], cut)
                if transcript is not None:
                    transcript.load(st["sid"])
                print(dim(L(f"Đã lùi lại {n} tin. Sửa và Enter để gửi lại (trống = hủy):", f"Rewound {n} message(s). Edit and press Enter to resend (empty = cancel):")))
                try:
                    edited = (reader(prompt_str) if reader else input(prompt_str)).strip() if interactive() else prior_text
                except (EOFError, KeyboardInterrupt):
                    print()
                    continue
                if not edited:
                    continue
                line, resend = edited, True
            elif cmd == "/compress":
                from ..services import compaction

                if not st["sid"]:
                    continue
                done = compaction.maybe_compact(st["sid"], cfg, st["provider"])
                print(dim(L("Đã nén hội thoại cũ." if done else "Hội thoại còn ngắn, chưa cần nén.",
                             "Older turns summarized." if done else "Conversation is short enough; nothing to compress.")))
            elif cmd == "/diff":
                import subprocess

                try:
                    out = subprocess.run(["git", "diff", "--stat", "HEAD"], capture_output=True, text=True, timeout=10, cwd=str(cfg.workdir) if hasattr(cfg, "workdir") else None).stdout.strip()
                except Exception as e:  # noqa: BLE001 - khong co git/khong phai repo thi bao loi gon
                    out = ""
                    print(red(str(e)))
                print(out or dim(L("Không có thay đổi.", "No changes.")))
            else:
                print(red(L("Lệnh không hợp lệ. Gõ /help.", "Unknown or invalid command. Type /help.")))
            if not resend:
                continue
        if transcript is None:
            print()
        effort = None if st["effort"] == "auto" else st["effort"]
        t0 = time.time()
        events = chat_runner.stream_chat(st["sid"], line, st["provider"], source="cli", permission=st["perm"], effort=effort)
        spinner = ThinkingSpinner(L("Nestor đang suy nghĩ...", "Nestor is thinking..."), terminal=terminal)
        try:
            with _busy_chat_footer(cfg, st, prompt_str, enabled=reader is not None, terminal=terminal):
                spinner.start()
                try:
                    res = consume(events, live=True, verbose=False, ask=True, spinner=spinner, transcript=transcript)
                finally:
                    spinner.stop(clear=True)
        except KeyboardInterrupt:
            print(dim(f"\n({L('đã dừng', 'stopped')})"))
            continue
        st["sid"] = res["session"] or st["sid"]
        if res["error"]:
            print(red(f"✗ {res['error']}"))
        elif res["provider"] and transcript is None:
            u = res["usage"]
            print(dim(f"  {res['provider']} · {time.time() - t0:.1f}s" + (f" · {u['prompt']}+{u['completion']} tokens" if u["prompt"] else "") + f" · {L('phiên', 'session')} {st['sid']}"))
        if transcript is not None:
            print()


__all__ = ["run", "chat", "green"]
