"""Điểm vào cho PyInstaller (không import theo đường dẫn tương đối nên chạy được khi đã đóng băng)."""
import sys

from nestor.desktop_server import main

if __name__ == "__main__":
    sys.exit(main())
