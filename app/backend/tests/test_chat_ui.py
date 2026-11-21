"""Kiểm thử ô nhập và nội dung chat đã gửi."""
import asyncio
from contextlib import redirect_stdout
from io import StringIO
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from prompt_toolkit import PromptSession
from prompt_toolkit.application import create_app_session
from prompt_toolkit.data_structures import Size
from prompt_toolkit.input import create_pipe_input
from prompt_toolkit.output import DummyOutput

from nestor.cli import chatcmd


def test_context_command_reads_latest_measurement_without_a_provider_call(tmp_env, capsys):
    from nestor.core import config
    from nestor.services import agent, sessions, usage

    cfg = config.load()
    name = cfg.default_provider
    pcfg = cfg.providers[name]
    sid = sessions.create("context")
    current = {"role": "user", "content": "Xin chào"}
    report = agent.context_report([{"role": "system", "content": "Chỉ dẫn"}, current], [], pcfg, current)
    usage.record_llm(name, pcfg.model, 1_234, 56, 100, True, sid, report)
    st = {"sid": sid, "provider": name, "perm": "default", "effort": "auto"}
    commands = iter(("/context", "/exit"))

    assert chatcmd._chat_loop(cfg, st, lambda _: next(commands)) == 0

    output = capsys.readouterr().out
    assert "1,234" in output and str(report["sections"]["current"]) in output


def test_interactive_reply_streams_then_renders_markdown_once():
    response = "Hôm nay là **Thứ Bảy**.\n\n- Một mục\n\n```python\nprint(1)\n```"
    terminal = StringIO()
    transcript = chatcmd._ChatTranscript(terminal)

    def events():
        yield {"type": "thinking", "text": "Temporary reasoning"}
        yield {"type": "tool", "name": "read", "args": {"path": "temporary.txt"}}
        yield {"type": "tool_result", "result": "Temporary result", "ok": True}
        yield {"type": "notice", "message": "Temporary notice"}
        yield {"type": "delta", "text": response[:20]}
        assert terminal.getvalue() == response[:20]
        yield {"type": "delta", "text": response[20:]}
        assert terminal.getvalue() == response
        yield {"type": "assistant", "content": response, "provider": "local", "usage": {"prompt": 2, "completion": 4}}

    with redirect_stdout(transcript), patch("nestor.cli.ui.COLOR", True), patch.dict("os.environ", {"TERM": "xterm-256color"}):
        result = chatcmd.consume(events(), live=True, verbose=False, ask=False, transcript=transcript)

    output = transcript.text()
    assert result["output"] == response
    assert terminal.getvalue() == response + "\n"
    assert output.count("Hôm nay là") == 1
    assert "Temporary" not in output and "temporary.txt" not in output
    assert "\x1b[1mThứ Bảy" in output
    assert "**" not in output and "```" not in output
    assert "•" in output and "Một mục" in output


@pytest.mark.parametrize(("keys", "expected"), [
    ("\x1b[B\r", "/model"),
    ("\x1b[B\x1b[C\r", "/perm"),
    ("\x1b[B\x1b[C\x1b[C\r", "/effort"),
    ("\x1b[B\x1b[D\r", "/open"),
    ("\x1b[B\x1b[Ahello\r", "hello"),
])
def test_footer_keyboard_navigation(keys, expected, capsys):
    cfg = SimpleNamespace(providers={"local": SimpleNamespace(model="test-model")})
    state = {"provider": "local", "perm": "default", "effort": "auto", "sid": None}
    transcript = chatcmd._ChatTranscript(StringIO())
    with (
        create_pipe_input() as terminal_input,
        create_app_session(input=terminal_input, output=DummyOutput()),
        patch("sys.stdin.isatty", return_value=True),
        patch("sys.stdout.isatty", return_value=True),
        patch("prompt_toolkit.shortcuts.prompt.is_dumb_terminal", return_value=False),
    ):
        terminal_input.send_text(keys)
        assert chatcmd._make_reader(cfg, state, transcript)("> ") == expected

    assert capsys.readouterr().out == ("> hello\n" if expected == "hello" else "")


def test_reader_erases_input_and_prints_submitted_message(capsys):
    with (
        create_pipe_input() as terminal_input,
        create_app_session(input=terminal_input, output=DummyOutput()),
        patch("sys.stdin.isatty", return_value=True),
        patch("sys.stdout.isatty", return_value=True),
        patch("nestor.cli.chatcmd.cyan", side_effect=lambda text: f"\x1b[36m{text}\x1b[0m"),
    ):
        cfg = SimpleNamespace(providers={"local": SimpleNamespace(model="test-model")})
        state = {"provider": "local", "perm": "default", "effort": "auto", "sid": None}
        reader = chatcmd._make_reader(cfg, state)
        terminal_input.send_text("first\\\rsecond\r")
        with patch.object(
            PromptSession, "prompt", autospec=True, side_effect=PromptSession.prompt
        ) as prompt:
            assert reader("> ") == "first\nsecond"
            assert prompt.call_args.args[0].app.erase_when_done
        assert capsys.readouterr().out == "> \x1b[36mfirst\n  second\x1b[0m\n"


@pytest.mark.parametrize(("scroll_input", "older_row"), [("\x1b[5~", 46), ("\x1b[<64;2;2M", 50)])
def test_scrolls_transcript_with_footer_still_on_screen(scroll_input, older_row):
    class RecordingOutput(DummyOutput):
        mouse_active = False

        def get_size(self):
            return Size(rows=12, columns=80)

        def enable_mouse_support(self):
            self.mouse_active = True

        def disable_mouse_support(self):
            self.mouse_active = False

    cfg = SimpleNamespace(providers={"local": SimpleNamespace(model="test-model")})
    state = {"provider": "local", "perm": "default", "effort": "auto", "sid": None}
    transcript = chatcmd._ChatTranscript(StringIO())
    transcript.write("".join(f"\x1b[2K\x1b[38;2;0;229;255mTranscript row {row:02d}\x1b[0m\n" for row in range(60)))
    screens = []
    styles = []
    output = RecordingOutput()
    mouse_states = []
    copied = []

    def observe(session, *args, **kwargs):
        def after_render(app):
            screen = app.renderer.last_rendered_screen
            if screen is not None and not app.is_done:
                screens.append(["".join(screen.data_buffer[y][x].char for x in range(80)) for y in range(12)])
                styles.append(screen.data_buffer[0][0].style)
                mouse_states.append(output.mouse_active)
                if len(screens) == 1:
                    terminal_input.send_text(scroll_input)
                elif len(screens) == 2:
                    terminal_input.send_text("\x1b[<0;1;1M\x1b[<32;10;1M\x1b[<0;10;1m")
                elif len(screens) in (3, 4):
                    terminal_input.send_text("\x1bOQ")
                elif len(screens) == 5:
                    terminal_input.send_text("hello\r")
        session.app.after_render += after_render
        session.app.pre_run_callables.append(
            lambda: asyncio.get_running_loop().call_later(
                1, lambda: not session.app.is_done and session.app.exit(exception=TimeoutError("missing scroll redraw"))
            )
        )
        return original_prompt(session, *args, set_exception_handler=False, **kwargs)

    original_prompt = PromptSession.prompt
    with (
        create_pipe_input() as terminal_input,
        create_app_session(input=terminal_input, output=output),
        patch("sys.stdin.isatty", return_value=True),
        patch("sys.stdout.isatty", return_value=True),
        patch("prompt_toolkit.shortcuts.prompt.is_dumb_terminal", return_value=False),
        patch.object(chatcmd, "_copy_selection", side_effect=lambda text, _: copied.append(text)),
        patch.object(PromptSession, "prompt", observe),
    ):
        assert chatcmd._make_reader(cfg, state, transcript)("> ") == "hello"

    latest, scrolled = screens[:2]
    assert any("Transcript row 59" in row for row in latest)
    assert not any("Transcript row 59" in row for row in scrolled)
    assert any(f"Transcript row {older_row}" in row for row in scrolled)
    assert all("#00e5ff" in style for style in styles[:5])
    assert "reverse" in styles[2]
    assert copied == ["Transcript"]
    assert mouse_states[:5] == [True, True, True, False, True]
    assert "F2" in screens[3][-1]
    for screen in (latest, scrolled):
        assert screen[-3].startswith("> ")
        assert "local / test-model" in screen[-1]


def test_model_picker_frames_are_excluded_from_transcript():
    cfg = SimpleNamespace(providers={
        "local": SimpleNamespace(model="test-model"),
        "remote": SimpleNamespace(model="remote-model"),
    })
    state = {"provider": "local", "perm": "default", "effort": "auto", "sid": None}
    terminal = StringIO()
    transcript = chatcmd._ChatTranscript(terminal)
    commands = iter(("/model", "/exit"))

    def choose(*_):
        print("model picker frame")
        print("model picker frame")
        return 1

    with redirect_stdout(transcript), patch.object(chatcmd, "choose", choose):
        assert chatcmd._chat_loop(cfg, state, lambda _: next(commands), transcript) == 0

    assert terminal.getvalue().count("model picker frame") == 2
    assert "model picker frame" not in transcript.text()
    assert "remote (remote-model)" in transcript.text()
    assert state["provider"] == "remote"


def test_open_picker_switches_the_transcript_to_the_selected_session():
    cfg = SimpleNamespace(providers={"local": SimpleNamespace(model="test-model")})
    state = {"provider": "local", "perm": "default", "effort": "auto", "sid": "old"}
    transcript = chatcmd._ChatTranscript(StringIO())
    transcript.write("Previous chat\n")
    commands = iter(("/open", "/exit"))
    recent = [{"id": "old", "title": "First"}, {"id": "next", "title": "Second"}]

    with (
        redirect_stdout(transcript),
        patch.object(chatcmd.sessions, "list_all", return_value=recent),
        patch.object(chatcmd.sessions, "get", return_value=recent[1]),
        patch.object(chatcmd.sessions, "messages", return_value=[{"role": "assistant", "content": "Selected chat"}]),
        patch.object(chatcmd, "choose", return_value=1),
    ):
        assert chatcmd._chat_loop(cfg, state, lambda _: next(commands), transcript) == 0

    assert state["sid"] == "next"
    assert "Selected chat" in transcript.text()
    assert "Previous chat" not in transcript.text()


def test_busy_footer_restores_terminal_on_interrupt(capsys):
    import os

    termios = pytest.importorskip("termios")
    cfg = SimpleNamespace(providers={"local": SimpleNamespace(model="test-model")})
    state = {"provider": "local", "perm": "default", "effort": "auto", "sid": "session-1"}
    previous = [0, 0, 0, termios.ECHO]

    with (
        patch("nestor.cli.chatcmd.tty", return_value=True),
        patch("nestor.cli.chatcmd.L", side_effect=lambda vi, en: en),
        patch.dict(os.environ, {"TERM": "xterm-256color"}),
        patch("sys.stdin.fileno", return_value=0),
        patch("shutil.get_terminal_size", return_value=os.terminal_size((80, 24))),
        patch.object(termios, "tcgetattr", return_value=previous),
        patch.object(termios, "tcsetattr") as set_attrs,
        pytest.raises(KeyboardInterrupt),
    ):
        with chatcmd._busy_chat_footer(cfg, state, "> ", enabled=True):
            assert set_attrs.call_args.args[2][3] & termios.ECHO == 0
            output = capsys.readouterr().out
            assert "\033[1;20r" in output
            assert "\033[22;1H\033[2K> Responding…" in output
            assert "local / test-model" in output
            status = next(line for line in output.split("\033[2K") if "local / test-model" in line)
            assert status.startswith("  local / test-model")
            assert status.index("Session session-1") + len("Session session-1") == 77
            raise KeyboardInterrupt

    set_attrs.assert_called_with(0, termios.TCSANOW, previous)
    assert "\033[r" in capsys.readouterr().out
