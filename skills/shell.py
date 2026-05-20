"""
skills/shell.py — Cross-platform shell access for Ptolemy.

:description:
    os.system() for fire-and-forget.
    os.popen() for captured output.
    SHELL dict maps logical commands to platform strings.
    No subprocess — minimal overhead.

:functions:
    run, capture, platform
:data:
    SHELL
"""

import os
import sys

_P = sys.platform

SHELL = {
    'clear':    'cls'         if _P == 'win32' else 'clear',
    'terminal': 'cmd.exe'     if _P == 'win32' else 'xterm',
    'open':     'start'       if _P == 'win32' else 'xdg-open',
    'which':    'where'       if _P == 'win32' else 'which',
    'home':     os.path.expanduser('~'),
    'null':     'NUL'         if _P == 'win32' else '/dev/null',
    'find':     'dir /s /b'   if _P == 'win32' else 'find',
    'xdotool':  ''            if _P == 'win32' else 'xdotool',
}


def run(cmd: str) -> int:
    """
    Fire-and-forget shell command.

    :param cmd: Shell command string.
    :returns: Exit code.
    :rtype: int
    """
    return os.system(cmd)


def capture(cmd: str) -> str:
    """
    Run command and return stdout as string.

    :param cmd: Shell command string.
    :returns: stdout output, stripped.
    :rtype: str
    """
    with os.popen(cmd) as fh:
        return fh.read()


def platform() -> str:
    """
    :returns: Platform string ('linux', 'darwin', 'win32').
    :rtype: str
    """
    return _P


def is_linux() -> bool:
    """:returns: True on Linux."""
    return _P == 'linux'


def is_mac() -> bool:
    """:returns: True on macOS."""
    return _P == 'darwin'


def is_windows() -> bool:
    """:returns: True on Windows."""
    return _P == 'win32'


def type_to_window(text: str, display: str = None):
    """
    Inject text into focused X11 window via xdotool.
    No-op on non-Linux.

    :param text: Text to type.
    :param display: X11 DISPLAY value (default: $DISPLAY).
    """
    if not is_linux():
        return
    disp = display or os.environ.get('DISPLAY', ':0')
    safe = text.replace('"', '\\"')
    run(f'DISPLAY={disp} xdotool type --clearmodifiers "{safe}"')


def key_to_window(combo: str, display: str = None):
    """
    Send key combination to focused X11 window via xdotool.

    :param combo: Key combo string e.g. 'ctrl+t', 'Return'.
    :param display: X11 DISPLAY value.
    """
    if not is_linux():
        return
    disp = display or os.environ.get('DISPLAY', ':0')
    run(f'DISPLAY={disp} xdotool key {combo}')
