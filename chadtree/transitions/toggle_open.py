from dataclasses import dataclass
from pathlib import PurePath
from shutil import which
from subprocess import CalledProcessError
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

from ..fs.ops import exists, new
from ..registry import rpc
from ..settings.localization import LANG
from ..settings.types import Settings
from ..state.types import State
from ..version_ctl.git import root as version_ctl_toplv
from .shared.current import maybe_path_above, new_current_file, new_root
from .shared.open_file import open_file
from .shared.wm import (
    find_current_buffer_path,
    find_fm_buffers,
    find_fm_windows_in_tab,
    find_windows_in_tab,
    new_fm_buffer,
    new_window,
    resize_fm_windows,
)
from .types import ClickType, Stage


@dataclass(frozen=True)
class _Args:
    path: Optional[PurePath]
    version_ctl: bool
    toggle: bool
    focus: bool


def _parse_args(args: Sequence[str]) -> _Args:
    parser = ArgParser()
    parser.add_argument("path", nargs="?", type=PurePath)
    parser.add_argument("--version-ctl", action="store_true")

    focus_group = parser.add_mutually_exclusive_group()
    focus_group.add_argument(
        "--always-focus", dest="toggle", action="store_false", default=True
    )
    focus_group.add_argument(
        "--nofocus", dest="focus", action="store_false", default=True
    )

    ns = parser.parse_args(args=args)
    opts = _Args(
        path=ns.path,
        version_ctl=ns.version_ctl,
        toggle=False if ns.version_ctl or ns.path else ns.toggle,
        focus=ns.focus,
    )
    return opts


def _ensure_side_window(
    nvim: Nvim, *, window: Window, settings: Settings, width: int
) -> None:
    open_left = settings.open_left
    windows = tuple(find_windows_in_tab(nvim, no_secondary=False))
    target = windows[0] if open_left else windows[-1]
    if window.number != target.number:
        if open_left:
            nvim.api.command("wincmd H")
        else:
            nvim.api.command("wincmd L")
        resize_fm_windows(nvim, width=width)


def _open_fm_window(nvim: Nvim, settings: Settings, opts: _Args, width: int) -> None:
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

        win = new_window(
            nvim,
            win_local=settings.win_actual_opts,
            open_left=settings.open_left,
            width=width,
        )
        for key, val in settings.win_local_opts.items():
            win_set_option(nvim, win=win, key=key, val=val)
        win_set_buf(nvim, win=win, buf=buf)

        _ensure_side_window(nvim, window=win, settings=settings, width=width)
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
        if opts.version_ctl:
            if which("git"):
                try:
                    cwd = version_ctl_toplv(state.root.path)
                    new_state = new_root(
                        nvim, state=state, settings=settings, new_cwd=cwd, indices=set()
                    )
                except CalledProcessError:
                    write(nvim, LANG("cannot find version ctl root"), error=True)
                    return None
            else:
                write(nvim, LANG("cannot find version ctl root"), error=True)
                return None
        else:
            new_state = state

        if opts.path:
            path = opts.path if opts.path.is_absolute() else get_cwd(nvim) / opts.path
            if not exists(path, follow=True):
                new(state.pool, paths=(path,))
            next_state = (
                maybe_path_above(nvim, state=new_state, settings=settings, path=path)
                or new_state
            )
            _open_fm_window(nvim, settings=settings, opts=opts, width=next_state.width)
            open_file(
                nvim,
                state=state,
                settings=settings,
                path=path,
                click_type=ClickType.primary,
            )
            return Stage(next_state, focus=path)
        else:
            curr = find_current_buffer_path(nvim)
            stage = (
                new_current_file(nvim, state=new_state, settings=settings, current=curr)
                if curr
                else None
            )
            _open_fm_window(nvim, settings=settings, opts=opts, width=new_state.width)
            return (
                Stage(stage.state, focus=curr)
                if stage
                else Stage(new_state, focus=curr)
            )
