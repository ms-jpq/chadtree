from argparse import ArgumentParser
from dataclasses import dataclass
from typing import NoReturn, Optional, Sequence

from pynvim import Nvim
from pynvim.api import Window
from pynvim_pp.lib import write

from ..registry import rpc
from ..settings.types import Settings
from ..state.types import State
from .shared.current import current
from .shared.wm import (
    find_current_buffer_name,
    find_fm_buffers,
    find_fm_windows_in_tab,
    find_windows_in_tab,
    new_fm_buffer,
    new_window,
    resize_fm_windows,
)
from .types import Stage


@dataclass(frozen=True)
class _OpenArgs:
    focus: bool


class _ArgparseError(Exception):
    pass


class _Argparse(ArgumentParser):
    def error(self, message: str) -> NoReturn:
        raise _ArgparseError(message)

    def exit(self, status: int = 0, message: Optional[str] = None) -> NoReturn:
        msg = self.format_help()
        raise _ArgparseError(msg)


def _parse_args(args: Sequence[str]) -> _OpenArgs:
    parser = _Argparse()
    parser.add_argument("--nofocus", dest="focus", action="store_false", default=True)

    ns = parser.parse_args(args=args)
    opts = _OpenArgs(focus=ns.focus)
    return opts


def _ensure_side_window(
    nvim: Nvim, *, window: Window, state: State, settings: Settings
) -> None:
    open_left = settings.open_left
    windows = tuple(find_windows_in_tab(nvim, no_preview=False))
    target = windows[0] if open_left else windows[-1]
    if window.number != target.number:
        if open_left:
            nvim.api.command("wincmd H")
        else:
            nvim.api.command("wincmd L")
        resize_fm_windows(nvim, state.width)


def _toggle_fm_window(
    nvim: Nvim, state: State, settings: Settings, opts: _OpenArgs
) -> None:
    cwin: Window = nvim.api.get_current_win()
    window = next(find_fm_windows_in_tab(nvim), None)
    if window:
        windows: Sequence[Window] = nvim.api.list_wins()
        if len(windows) <= 1:
            pass
        else:
            nvim.api.win_close(window, True)
    else:
        buffer = next(find_fm_buffers(nvim), None)
        if buffer is None:
            buffer = new_fm_buffer(nvim, keymap=settings.keymap)

        window = new_window(nvim, open_left=settings.open_left, width=state.width)
        for option, value in settings.win_local_opts.items():
            nvim.api.win_set_option(window, option, value)
        nvim.api.win_set_buf(window, buffer)

        _ensure_side_window(nvim, window=window, state=state, settings=settings)
        if not opts.focus:
            nvim.api.set_current_win(cwin)


@rpc(blocking=False)
def _open(
    nvim: Nvim, state: State, settings: Settings, args: Sequence[str]
) -> Optional[Stage]:
    """
    Toggle sidebar
    """

    try:
        opts = _parse_args(args)
    except _ArgparseError as e:
        write(nvim, e, error=True)
        return None
    else:
        curr = find_current_buffer_name(nvim)
        _toggle_fm_window(nvim, state=state, settings=settings, opts=opts)

        stage = current(nvim, state=state, settings=settings, current=curr)
        if stage:
            return stage
        else:
            return Stage(state)
