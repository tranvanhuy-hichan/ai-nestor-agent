"""nestor chat (REPL) va nestor run (mot lan): chay agent ngay trong tien trinh, khong can server."""
import json
import select
import shutil
import sys
import threading
import time

from ..services import api_run, chat_runner, sessions
from . import runtime
from .ui import L, ask_yes_no, bold, choose, cyan, dim, err, green, interactive, red, yellow

KIND = {"exec": ("chạy lệnh shell", "run a shell command"), "mcp": ("gọi tool MCP", "call an MCP tool"), "file_read": ("đọc file ngoài workspace", "read a file outside the workspace"),
        "file_write": ("ghi file", "write a file"), "http_request": ("gửi yêu cầu HTTP thay đổi dữ liệu", "send a state-changing HTTP request")}
PERMS = ("default", "readonly", "guarded", "full", "plan")
EFFORTS = ("auto", "low", "medium", "high", "thinking")


class ThinkingSpinner:
    """Hieu ung animation spinner khi Nestor / model dang suy nghi hoac goi tool."""
    FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    def __init__(self, message: str = "Nestor đang suy nghĩ..."):
        self.message = message
        self._stop = threading.Event()
        self._active = False
        self._thread: threading.Thread | None = None
        self._t0 = time.time()
        self._isatty = sys.stdout.isatty()
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
            line = f"\r  {cyan(frame)} {dim(self.message)}{dim(sec)} \033[K"
            with self._lock:
                if self._stop.is_set():
                    break
                try:
                    sys.stdout.write(line)
                    sys.stdout.flush()
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
                    sys.stdout.write("\r\033[K")
                    sys.stdout.flush()
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


def consume(events, *, live: bool, verbose: bool, ask: bool, deadline: float | None = None, spinner: ThinkingSpinner | None = None) -> dict:
    """Doc su kien tu stream_chat. live=True: in chu khi model dang sinh; ask=True: hoi y/N khi can phe duyet."""
    out = {"session": None, "output": "", "error": None, "timed_out": False, "provider": None, "usage": {"prompt": 0, "completion": 0}}
    streamed = False
    in_thinking = False
    try:
        for ev in events:
            t = ev["type"]
            if t == "session":
                out["session"] = ev["id"]
            elif t == "status":
                msg = ev.get("text") or ev.get("message") or ""
                if msg and spinner:
                    spinner.set_message(msg)
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
                sys.stdout.write(ev["text"])
                sys.stdout.flush()
                streamed = True
            elif t == "assistant":
                if spinner:
                    spinner.stop(clear=True)
                if in_thinking:
                    in_thinking = False
                    sys.stdout.write("\n\n")
                    sys.stdout.flush()
                out["output"], out["provider"] = ev["content"], ev["provider"]
                out["usage"] = {k: out["usage"][k] + ev["usage"][k] for k in out["usage"]}
                if live and streamed:
                    sys.stdout.write("\n")
                    sys.stdout.flush()
                elif live and ev["content"]:
                    sys.stdout.write(ev["content"] + "\n")
                    sys.stdout.flush()
                streamed = False
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
                print(f"\n{yellow('⚠')} {L('Agent muốn', 'The agent wants to')} {bold(L(label[0], label[1]))}:\n  {ev['detail'][:500]}", file=sys.stderr if not live else sys.stdout)
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


def get_cursor_row() -> int | None:
    """Lấy dòng hiện tại của con trỏ terminal qua mã ANSI DSR (Device Status Report: \\033[6n)."""
    if not (sys.stdin.isatty() and sys.stdout.isatty()):
        return None
    try:
        import os
        import termios
        import tty

        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            sys.stdout.write("\033[6n")
            sys.stdout.flush()
            resp = b""
            while True:
                r, _, _ = select.select([fd], [], [], 0.15)
                if not r:
                    break
                chunk = os.read(fd, 32)
                if not chunk:
                    break
                resp += chunk
                if b"R" in resp:
                    break
            text = resp.decode("ascii", "ignore")
            if "\033[" in text and "R" in text:
                part = text.split("\033[", 1)[1].split("R", 1)[0]
                if ";" in part:
                    row_str = part.split(";")[0]
                    if row_str.isdigit():
                        return int(row_str)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
    except Exception:
        return None
    return None


def pad_to_bottom(reserve_lines: int = 3) -> None:
    """Đẩy con trỏ xuống sát đáy terminal để hộp nhập chat luôn hiển thị ở dưới màn hình giống Claude Code."""
    if not (sys.stdin.isatty() and sys.stdout.isatty()):
        return
    try:
        lines = shutil.get_terminal_size((80, 24)).lines
        row = get_cursor_row()
        if row is not None:
            target_row = max(1, lines - reserve_lines + 1)
            if row < target_row:
                sys.stdout.write("\n" * (target_row - row))
                sys.stdout.flush()
    except Exception:
        pass


def _make_reader(cfg, st):
    """Trả về hàm đọc dòng có giao diện hộp nhập dưới cùng phong cách Claude Code (kèm autocomplete lệnh)."""
    try:
        from prompt_toolkit import PromptSession
        from prompt_toolkit.completion import Completer, Completion
        from prompt_toolkit.filters import Condition
        from prompt_toolkit.formatted_text import ANSI
        from prompt_toolkit.history import InMemoryHistory
        from prompt_toolkit.layout.containers import ConditionalContainer, Window
        from prompt_toolkit.layout.controls import FormattedTextControl
    except ImportError:
        return None
    if not (sys.stdin.isatty() and sys.stdout.isatty()):
        return None

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

    class ClaudePromptSession(PromptSession):
        def __init__(self, *args, **kwargs):
            self.show_borders = True
            super().__init__(*args, **kwargs)

        def _create_layout(self):
            layout = super()._create_layout()
            main_split = layout.container.children[0]
            hsplit = main_split.content if hasattr(main_split, "content") else main_split

            def get_bottom_border():
                cols = shutil.get_terminal_size((80, 24)).columns
                return ANSI(f"\033[90m{'─' * cols}\033[0m")

            bottom_window = ConditionalContainer(
                Window(
                    FormattedTextControl(get_bottom_border),
                    dont_extend_height=True,
                    height=1,
                ),
                filter=Condition(lambda: self.show_borders),
            )
            hsplit.children.append(bottom_window)
            return layout

    session = ClaudePromptSession(
        completer=SlashCompleter(),
        complete_while_typing=True,
        history=InMemoryHistory(),
        reserve_space_for_menu=0,
    )

    def read(first: str = "", cont: str = "") -> str:
        cols = shutil.get_terminal_size((80, 24)).columns
        border = "─" * cols
        top_line = f"\033[90m{border}\033[0m\n"
        prompt_text = first or (f"\033[36m>\033[0m " if not cont else cont)
        if not cont:
            session.show_borders = True
            msg = ANSI(top_line + prompt_text)
        else:
            session.show_borders = False
            msg = ANSI(cont)

        res = session.prompt(msg)
        if not cont and sys.stdout.isatty():
            try:
                curr_cols = shutil.get_terminal_size((80, 24)).columns
                sys.stdout.write(f"\033[90m{'─' * curr_cols}\033[0m\n")
                sys.stdout.flush()
            except Exception:
                pass
        return res

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
    print_chat_banner(cfg, st["provider"], st["perm"], st["sid"])
    reader = _make_reader(cfg, st)
    prompt_str = f"{cyan('>')} "
    while True:
        try:
            pad_to_bottom(reserve_lines=3)
            if reader:
                line = reader(prompt_str, "").strip()
                while line.endswith("\\"):
                    line = line[:-1] + "\n" + reader("", dim("  … ")).rstrip()
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
            elif cmd == "/new":
                st["sid"] = None
                print(dim(L("Đã bắt đầu hội thoại mới.", "Started a new conversation.")))
            elif cmd == "/sessions":
                for s in sessions.list_all(10):
                    print(f"  {s['id']}  {s['title'][:50]}  {dim(time.strftime('%m-%d %H:%M', time.localtime(s['updated'])))}")
            elif cmd == "/open" and sessions.get(rest):
                st["sid"] = rest
                print(dim(L(f"Đã mở {rest} ({len(sessions.messages(rest))} tin).", f"Opened {rest} ({len(sessions.messages(rest))} messages).")))
            elif cmd == "/model":
                names = list(cfg.providers)
                if not rest:
                    opts = [(f"{'●' if n == st['provider'] else ' '} {n}", cfg.providers[n].model or cfg.providers[n].type) for n in names]
                    try:
                        rest = names[choose(L("Chọn model", "Pick a model"), opts, names.index(st["provider"]) if st["provider"] in names else 0)]
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
                    st[key] = vals[choose(L("Chọn quyền", "Pick permissions") if key == "perm" else L("Chọn mức suy nghĩ", "Pick effort"), [("● " if v == st[key] else "  ") + v for v in vals], vals.index(st[key]) if st[key] in vals else 0)]
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
                print(dim(L(f"Đã lùi lại {n} tin. Sửa và Enter để gửi lại (trống = hủy):", f"Rewound {n} message(s). Edit and press Enter to resend (empty = cancel):")))
                try:
                    edited = (reader(prompt_str, "") if reader else input(prompt_str)).strip() if interactive() else prior_text
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
        print()
        effort = None if st["effort"] == "auto" else st["effort"]
        t0 = time.time()
        events = chat_runner.stream_chat(st["sid"], line, st["provider"], source="cli", permission=st["perm"], effort=effort)
        spinner = ThinkingSpinner(L("Nestor đang suy nghĩ...", "Nestor is thinking..."))
        spinner.start()
        try:
            res = consume(events, live=True, verbose=False, ask=True, spinner=spinner)
        except KeyboardInterrupt:
            print(dim(f"\n({L('đã dừng', 'stopped')})"))
            continue
        finally:
            spinner.stop(clear=True)
        st["sid"] = res["session"] or st["sid"]
        if res["error"]:
            print(red(f"✗ {res['error']}"))
        elif res["provider"]:
            u = res["usage"]
            print(dim(f"  {res['provider']} · {time.time() - t0:.1f}s" + (f" · {u['prompt']}+{u['completion']} tokens" if u["prompt"] else "") + f" · {L('phiên', 'session')} {st['sid']}"))


__all__ = ["run", "chat", "green"]
