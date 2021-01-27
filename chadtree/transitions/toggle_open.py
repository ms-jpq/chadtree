from dataclasses import dataclass
from os.path import exists, isabs, join, realpath
from typing import Optional, Sequence

from pynvim import Nvim
from pynvim.api import Window
from pynvim_pp.api import (
    cur_win,
    get_cwd,
    list_wins,
    set_cur_win,
    win_close,
    win_set_buf,
    win_set_option,
)
from pynvim_pp.lib import write
from std2.argparse import ArgparseError, ArgParser

from ..registry import rpc
from ..settings.localization import LANG
from ..settings.types import Settings
from ..state.types import State
from .shared.current import maybe_path_above, new_current_file
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
class _Args:
    path: Optional[str]
    toggle: bool
    focus: bool


def _parse_args(args: Sequence[str]) -> _Args:
    parser = ArgParser()
    parser.add_argument("path", nargs="?")

    focus_group = parser.add_mutually_exclusive_group()
    focus_group.add_argument(
        "--always-focus", dest="toggle", action="store_false", default=True
    )
    focus_group.add_argument(
        "--nofocus", dest="focus", action="store_false", default=True
    )

    ns = parser.parse_args(args=args)
    opts = _Args(path=ns.path, toggle=False if ns.path else ns.toggle, focus=ns.focus)
    return opts


def _ensure_side_window(
    nvim: Nvim, *, window: Window, state: State, settings: Settings
) -> None:
    open_left = settings.open_left
    windows = tuple(find_windows_in_tab(nvim, no_secondary=False))
    target = windows[0] if open_left else windows[-1]
    if window.number != target.number:
        if open_left:
            nvim.api.command("wincmd H")
        else:
            nvim.api.command("wincmd L")
        resize_fm_windows(nvim, state.width)


def _open_fm_window(nvim: Nvim, state: State, settings: Settings, opts: _Args) -> None:
    cwin = cur_win(nvim)
    win = next(find_fm_windows_in_tab(nvim), None)
    if win:
        if opts.toggle:
            wins = list_wins(nvim)
            if len(wins) > 1:
                win_close(nvim, win=win)
        else:
            set_cur_win(nvim, win=win)
    else:
        buf = next(find_fm_buffers(nvim), None)
        if buf is None:
            buf = new_fm_buffer(nvim, settings=settings)

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
        raw_path = opts.path
        if raw_path:
            path = realpath(
                raw_path if isabs(raw_path) else join(get_cwd(nvim), raw_path)
            )
            if not exists(path):
                write(nvim, LANG("path not exist", path=path))
                return None
            else:
                new_state = (
                    maybe_path_above(nvim, state=state, settings=settings, path=path)
                    or state
                )
                _open_fm_window(nvim, state=new_state, settings=settings, opts=opts)
                return Stage(new_state, focus=path)
        else:
            curr = find_current_buffer_name(nvim)
            stage = new_current_file(nvim, state=state, settings=settings, current=curr)
            _open_fm_window(nvim, state=state, settings=settings, opts=opts)
            return stage if stage else Stage(state, focus=curr)
