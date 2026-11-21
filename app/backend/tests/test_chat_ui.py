"""Kiem thu giao dien chat CLI: o nhap duoi day man hinh giong Claude Code."""
import sys
from unittest.mock import MagicMock, patch

from nestor.cli import chatcmd


def test_cursor_row_non_tty():
    # Khong phai tty thi luon tra ve None ma khong gay block/hang
    with patch("sys.stdin.isatty", return_value=False), patch("sys.stdout.isatty", return_value=False):
        assert chatcmd.get_cursor_row() is None


def test_pad_to_bottom_positions_at_bottom():
    # Khi con tro o dong 10, terminal 24 dong, reserve 3 dong (line tren + prompt + line duoi):
    # target = 24 - 3 + 1 = 22 -> can 22 - 10 = 12 dau \n
    written = []
    with patch("sys.stdin.isatty", return_value=True), patch("sys.stdout.isatty", return_value=True), \
         patch("nestor.cli.chatcmd.get_cursor_row", return_value=10), \
         patch("shutil.get_terminal_size", return_value=MagicMock(lines=24, columns=80)), \
         patch("sys.stdout.write", side_effect=written.append), \
         patch("sys.stdout.flush"):
        chatcmd.pad_to_bottom(reserve_lines=3)
        assert "".join(written) == "\n" * 12


def test_pad_to_bottom_already_at_bottom_no_unnecessary_scroll():
    # Khi con tro da o dong 23/24, khong in them \n tranh day output cu troi mat
    written = []
    with patch("sys.stdin.isatty", return_value=True), patch("sys.stdout.isatty", return_value=True), \
         patch("nestor.cli.chatcmd.get_cursor_row", return_value=23), \
         patch("shutil.get_terminal_size", return_value=MagicMock(lines=24, columns=80)), \
         patch("sys.stdout.write", side_effect=written.append), \
         patch("sys.stdout.flush"):
        chatcmd.pad_to_bottom(reserve_lines=3)
        assert "".join(written) == ""


def test_make_reader_slash_completer():
    cfg = MagicMock()
    cfg.providers = {"openai": MagicMock(model="gpt-4o", type="openai"), "anthropic": MagicMock(model="claude-3-5-sonnet", type="anthropic")}
    st = {"provider": "openai"}

    with patch("sys.stdin.isatty", return_value=True), patch("sys.stdout.isatty", return_value=True):
        reader = chatcmd._make_reader(cfg, st)
        assert callable(reader)
