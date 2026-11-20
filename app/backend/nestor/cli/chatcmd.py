"""nestor chat (REPL) va nestor run (mot lan): chay agent ngay trong tien trinh, khong can server."""
import json
import sys
import threading
import time

from ..services import api_run, chat_runner, sessions
from . import runtime
from .ui import L, ask_yes_no, bold, cyan, dim, err, green, interactive, red, yellow

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
            self._thread.join(timeout=0.2)
        self._active = False
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
    try:
        for ev in events:
            t = ev["type"]
            if t == "session":
                out["session"] = ev["id"]
            elif t == "delta" and live:
                if spinner:
                    spinner.stop(clear=True)
                print(ev["text"], end="", flush=True)
                streamed = True
            elif t == "thinking":
                if spinner:
                    spinner.set_message(L("Nestor đang suy nghĩ...", "Nestor is thinking..."))
                if verbose:
                    print(dim(ev["text"]), end="", file=sys.stderr, flush=True)
            elif t == "assistant":
                if spinner:
                    spinner.stop(clear=True)
                out["output"], out["provider"] = ev["content"], ev["provider"]
                out["usage"] = {k: out["usage"][k] + ev["usage"][k] for k in out["usage"]}
                if live and streamed:
                    print()
                elif live and ev["content"]:
                    print(ev["content"])
                streamed = False
            elif t in ("tool", "tool_result") and (verbose or live):
                if spinner:
                    spinner.stop(clear=True)
                line = _trace(ev)
                if line:
                    print(dim(line), file=sys.stdout if live else sys.stderr, flush=True)
                if spinner and t == "tool":
                    spinner.start(L(f"Đang thực hiện {ev.get('name', 'tool')}...", f"Running {ev.get('name', 'tool')}..."))
            elif t == "approval":
                if spinner:
                    spinner.stop(clear=True)
                label = KIND.get(ev["kind"], (ev["kind"], ev["kind"]))
                print(f"\n{yellow('⚠')} {L('Agent muốn', 'The agent wants to')} {bold(L(label[0], label[1]))}:\n  {ev['detail'][:500]}", file=sys.stderr if not live else sys.stdout)
                allowed = ask and ask_yes_no(L("Cho phép?", "Allow?"), False)
                chat_runner.resolve_approval(ev["id"], allowed)
            elif t == "notice" and (verbose or live):
                print(dim(f"· {ev['message']}"), file=sys.stderr if not live else sys.stdout)
            elif t == "error":
                if spinner:
                    spinner.stop(clear=True)
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
        res = consume(events, live=False, verbose=args.verbose, ask=args.ask, deadline=time.time() + args.timeout, spinner=spinner)
    finally:
        spinner.stop(clear=True)
    if res["output"]:
        print(res["output"])
    if res["error"]:
        err(res["error"])
        return 1
    return 0


HELP = {
    "/help": ("Hiện trợ giúp", "Show help"), "/new": ("Bắt đầu hội thoại mới", "Start a new conversation"), "/sessions": ("Liệt kê hội thoại gần đây", "List recent conversations"),
    "/open <id>": ("Mở lại một hội thoại", "Reopen a conversation"), "/model <name>": ("Đổi provider", "Switch provider"), "/perm <mode>": ("default | readonly | guarded | full", "default | readonly | guarded | full"),
    "/effort <level>": ("auto | low | medium | high | thinking", "auto | low | medium | high | thinking"), "/skills": ("Liệt kê skill", "List skills"), "/files": ("Liệt kê file của phiên", "List the conversation's files"), "/exit": ("Thoát (hoặc Ctrl+D)", "Quit (or Ctrl+D)"),
}


def _make_reader(cfg, st):
    """Tra ve ham doc 1 dong. Co prompt_toolkit: go "/" la hien menu goi y lenh (kem mo ta). Khong co: input() thuong."""
    try:
        from prompt_toolkit import PromptSession
        from prompt_toolkit.completion import Completer, Completion
        from prompt_toolkit.formatted_text import ANSI
        from prompt_toolkit.history import InMemoryHistory
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
                opts = [(n, "") for n in cfg.providers]
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

    session = PromptSession(completer=SlashCompleter(), complete_while_typing=True, history=InMemoryHistory(), reserve_space_for_menu=8)

    def read(first: str, cont: str) -> str:
        return session.prompt(ANSI(first if not cont else cont))

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
    while True:
        try:
            if reader:
                print()
                line = reader(f"{cyan(st['provider'])} {bold('›')} ", "").strip()
                while line.endswith("\\"):
                    line = line[:-1] + "\n" + reader("", dim("  … ")).rstrip()
            else:
                print(f"\n{cyan(st['provider'])} {bold('›')} ", end="", flush=True)
                line = input().strip()
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
            elif cmd == "/model" and rest in cfg.providers:
                st["provider"] = rest
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
            else:
                print(red(L("Lệnh không hợp lệ. Gõ /help.", "Unknown or invalid command. Type /help.")))
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
