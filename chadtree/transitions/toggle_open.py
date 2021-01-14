from dataclasses import dataclass
from typing import Optional, Sequence

from pynvim import Nvim
from pynvim.api import Window
from pynvim_pp.api import (
    cur_win,
    list_wins,
    set_cur_win,
    win_close,
    win_set_buf,
    win_set_option,
)
from pynvim_pp.lib import write
from std2.argparse import ArgparseError, ArgParser

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


def _parse_args(args: Sequence[str]) -> _OpenArgs:
    parser = ArgParser()
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
    cwin = cur_win(nvim)
    win = next(find_fm_windows_in_tab(nvim), None)
    if win:
        wins = list_wins(nvim)
        if len(wins) <= 1:
            pass
        else:
            win_close(nvim, win=win)
    else:
        buf = next(find_fm_buffers(nvim), None)
        if buf is None:
            buf = new_fm_buffer(nvim, keymap=settings.keymap)

        win = new_window(nvim, open_left=settings.open_left, width=state.width)
        for key, val in settings.win_local_opts.items():
            win_set_option(nvim, win=win, key=key, val=val)
        win_set_buf(nvim, win=win, buf=buf)

        _ensure_side_window(nvim, window=win, state=state, settings=settings)
        if not opts.focus:
            set_cur_win(nvim, win=cwin)


@rpc(blocking=False)
def _open(
    nvim: Nvim, state: State, settings: Settings, args: Sequence[str]
) -> Optional[Stage]:
    """
    Toggle sidebar
    """

    try:
        opts = _parse_args(args)
    except ArgparseError as e:
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
