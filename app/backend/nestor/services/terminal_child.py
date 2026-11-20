"""Attach an already isolated child process to the terminal before starting its shell."""
import os
import shutil


def run():
    import fcntl
    import termios

    fcntl.ioctl(0, termios.TIOCSCTTY, 0)
    shell = shutil.which("bash") or "/bin/sh"
    os.execv(shell, [shell, "-i"])


if __name__ == "__main__":
    run()
