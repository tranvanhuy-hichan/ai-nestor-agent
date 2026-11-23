"""Kiem thu menu chon bang phim tren terminal ao (pty): mui ten, Space, Enter, End, Co/Khong."""
import fcntl
import json
import os
import pty
import re
import select
import socket
import struct
import sys
import termios
import time
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(os.name != "posix", reason="can terminal POSIX")
BACKEND = Path(__file__).resolve().parents[1]
ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")
UP, DOWN, RIGHT, LEFT, END = b"\x1b[A", b"\x1b[B", b"\x1b[C", b"\x1b[D", b"\x1b[F"


class Pty:
    def __init__(self, argv: list[str], env: dict[str, str]):
        self.pid, self.fd = pty.fork()
        if self.pid == 0:
            os.execvpe(argv[0], argv, env)
        fcntl.ioctl(self.fd, termios.TIOCSWINSZ, struct.pack("HHHH", 30, 110, 0, 0))
        self.text = ""

    def read_until(self, needle: str, timeout: float = 20) -> None:
        end = time.time() + timeout
        while needle not in ANSI.sub("", self.text):
            if time.time() > end:
                raise AssertionError(f"khong thay {needle!r}. Man hinh cuoi:\n{ANSI.sub('', self.text)[-900:]}")
            if select.select([self.fd], [], [], 0.1)[0]:
                try:
                    self.text += os.read(self.fd, 4096).decode("utf-8", "replace")
                except OSError:
                    break

    def send(self, data: bytes) -> None:
        time.sleep(0.15)  # cho menu ve xong, giong toc do go cua nguoi
        os.write(self.fd, data)

    def mark(self) -> None:
        self.text = ""

    def finish(self, timeout: float = 20) -> int:
        end = time.time() + timeout
        while time.time() < end:
            if select.select([self.fd], [], [], 0.1)[0]:
                try:
                    self.text += os.read(self.fd, 4096).decode("utf-8", "replace")
                except OSError:  # pty dong khi tien trinh thoat; van phai lay ma thoat o duoi
                    pass
            done, status = os.waitpid(self.pid, os.WNOHANG)
            if done:
                return os.waitstatus_to_exitcode(status)
        os.kill(self.pid, 9)
        raise AssertionError("tien trinh khong thoat. Man hinh cuoi:\n" + ANSI.sub("", self.text)[-600:])


def env_for(home: Path, lang: str) -> dict[str, str]:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    return {**os.environ, "NESTOR_HOME": str(home), "NESTOR_PORT": str(port), "NESTOR_LANG": lang, "PYTHONPATH": str(BACKEND), "TERM": "xterm-256color", "NO_COLOR": ""}


def test_chat_keeps_alternate_screen_open_while_streaming(tmp_path):
    script = """
from nestor.cli import main
from nestor.services import chat_runner

def stream_chat(*args, **kwargs):
    yield {"type": "delta", "text": "Reply inside chat"}
    yield {"type": "delta", "text": r" $O(n \\times W)$"}
    yield {"type": "assistant", "content": r"Reply inside chat $O(n \\times W)$", "provider": "local",
           "usage": {"prompt": 1, "completion": 1}}

chat_runner.stream_chat = stream_chat
print("Shell before chat", flush=True)
try:
    main()
finally:
    print("Shell after chat", flush=True)
"""
    p = Pty([sys.executable, "-c", script, "chat"], env_for(tmp_path, "en"))
    p.read_until("Ctrl+D to exit")
    p.send(b"hello\r")
    p.read_until("Reply inside chat")
    p.read_until("O(n × W)")
    p.send(b"/exit\r")
    p.read_until("Shell after chat")
    assert p.finish() == 0, ANSI.sub("", p.text)[-900:]
    enter, leave = "\x1b[?1049h", "\x1b[?1049l"
    assert p.text.count(enter) == p.text.count(leave) == 1
    before, chat = p.text.split(enter)
    chat, after = chat.split(leave)
    assert "Shell before chat" in ANSI.sub("", before)
    assert "Reply inside chat" in ANSI.sub("", chat)
    assert chat.startswith("\x1b[?1007s\x1b[?1007l")
    assert chat.endswith("\x1b[?1007r")
    assert "Shell after chat" in ANSI.sub("", after)


def test_chat_scrolls_while_waiting_and_streaming(tmp_path):
    script = r"""
import os
import time
from pathlib import Path

from nestor.cli import main
from nestor.services import chat_runner

def stream_chat(sid, prompt, *args, **kwargs):
    if prompt == "first question":
        reply = "\n".join(f"Earlier reply row {row:02d}" for row in range(45))
        reply = "```\n" + reply + "\n```"
    else:
        marker = Path(os.environ["NESTOR_HOME"]) / "finish-reply"
        end = time.monotonic() + 8
        while not marker.exists() and time.monotonic() < end:
            time.sleep(0.05)
        first_chunk = "Second reply is streaming."
        yield {"type": "delta", "text": first_chunk}
        finish = marker.with_name("end-stream")
        end = time.monotonic() + 8
        while not finish.exists() and time.monotonic() < end:
            time.sleep(0.05)
        last_chunk = " Second reply is ready."
        yield {"type": "delta", "text": last_chunk}
        reply = first_chunk + last_chunk
    if prompt == "first question":
        yield {"type": "delta", "text": reply}
    yield {"type": "assistant", "content": reply, "provider": "local",
           "usage": {"prompt": 1, "completion": 1}}

chat_runner.stream_chat = stream_chat
main(["chat"])
"""
    p = Pty([sys.executable, "-c", script], env_for(tmp_path, "en"))
    p.read_until("Ctrl+D to exit")
    p.send(b"first question\r")
    p.read_until("Earlier reply row 44")
    p.send(b"second question\r")
    p.read_until("Responding…")
    p.mark()
    p.send(b"\x1b[<64;2;4M" * 8)
    p.read_until("Earlier reply row 05", timeout=4)
    assert re.search(r"\x1b\[[0-9;]*mEarlier reply row 05", p.text)
    assert "Second reply is streaming" not in p.text
    p.send(b"\x1b[<65;2;4M" * 8)
    p.read_until("Earlier reply row 44")
    (tmp_path / "finish-reply").touch()
    p.read_until("Second reply is streaming")
    p.mark()
    p.send(b"\x1b[<64;2;4M" * 8)
    p.read_until("Earlier reply row 05", timeout=4)
    assert re.search(r"\x1b\[[0-9;]*mEarlier reply row 05", p.text)
    p.send(b"\x1b[<65;2;4M" * 8)
    p.read_until("Second reply is streaming")
    (tmp_path / "end-stream").touch()
    p.read_until("Second reply is ready")
    p.send(b"/exit\r")
    assert p.finish() == 0, ANSI.sub("", p.text)[-900:]


def test_onboard_language_menu_back_and_save(tmp_path):
    p = Pty([sys.executable, "-m", "nestor", "onboard"], env_for(tmp_path, "en"))
    p.read_until("Language / Ngôn ngữ")
    p.send(UP + b"\r")
    p.read_until("Thiết lập Nestor")
    p.send(DOWN + b"\r")
    p.mark()
    p.read_until("Đổi thư mục workspace")
    p.send(b"\r")
    p.read_until("Thư mục workspace [workspace]")
    p.send(b"project\r")
    p.read_until("Đổi thư mục workspace")
    p.send(b"2\r")
    p.read_until("Bạn tên là gì")
    p.send(b"Ann\r")
    p.send(b"\x1b")
    p.read_until("Thiết lập Nestor")
    p.send(b"4\r")
    p.read_until("Web search · DuckDuckGo")
    p.send(b"\r")
    p.read_until("❯ Bật")
    p.send(DOWN + b"\r")
    p.send(b"\x1b")
    p.send(END + UP + b"\r")
    assert p.finish() == 0
    cfg = json.loads((tmp_path / "config.json").read_text())
    assert cfg["language"] == "vi"
    assert cfg["agent"]["workspace"] == "project"
    assert cfg["agent"]["tools_enabled"]["web_search"] is False
    assert cfg["agent"]["confirm_exec"] is True
    assert "Ann" in (tmp_path / "project" / "USER.md").read_text()
    assert not (tmp_path / "data" / "server.pid").exists()


def test_onboard_back_then_exit_preserves_saved_config(tmp_path):
    path = tmp_path / "config.json"
    original = '{"language":"vi","agent":{"confirm_exec":false}}'
    path.write_text(original)
    p = Pty([sys.executable, "-m", "nestor", "onboard", "--language", "en"], env_for(tmp_path, "en"))
    p.read_until("Nestor setup")
    p.send(b"5\r")
    p.read_until("Shell command approval")
    p.send(b"\r")
    p.read_until("❯ Off")
    p.send(UP + b"\r")
    p.send(END + b"\r")
    p.send(END + b"\r")
    assert p.finish() == 0
    assert path.read_text() == original


def test_multiselect_all_with_a_key_then_interrupt_exits_cleanly(tmp_path):
    script = "from nestor.cli.ui import multiselect; multiselect('Select options', ['First', 'Second'])"
    p = Pty([sys.executable, "-c", script], env_for(tmp_path, "en"))
    p.read_until("Space toggle")
    p.send(b"a")
    p.read_until("◼")
    p.send(b"\x03")
    assert p.finish() != 0


def test_onboard_daemon_uses_selected_port_after_returning_to_main_menu(tmp_path):
    script = """
from nestor.cli import main
from nestor.cli import daemon
from nestor.core.config import load

def start(host, port):
    assert load().language == "en"
    print(f"Selected address: {host}:{port}")
    return 0

daemon.start = start
main()
"""
    p = Pty([sys.executable, "-c", script, "onboard", "--language", "en", "--start"], env_for(tmp_path, "en"))
    p.read_until("Nestor setup")
    p.send(END + UP + UP + b"\r")
    p.read_until("Address and port for this launch")
    p.send(DOWN + b"\r")
    p.read_until("Listen address")
    p.send(b"\r")
    p.read_until("Port [")
    p.send(b"18787\r")
    p.send(b"\x1b")
    p.send(END + UP + b"\r")
    assert p.finish() == 0
    assert "Selected address: 127.0.0.1:18787" in ANSI.sub("", p.text)
