from dataclasses import dataclass
from pathlib import PurePath
from subprocess import CalledProcessError
from typing import Mapping, Optional, Sequence

from pynvim_pp.nvim import Nvim
from pynvim_pp.types import ExtData
from pynvim_pp.window import Window
from std2 import anext
from std2.argparse import ArgparseError, ArgParser

from ..fs.ops import exists, new, which
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


async def _ensure_side_window(
    *,
    settings: Settings,
    window_order: Mapping[ExtData, None],
    width: int,
    window: Window,
) -> None:
    open_left = settings.open_left
    windows = [
        win
        async for win in find_windows_in_tab(last_used=window_order, no_secondary=False)
    ]
    target = windows[0] if open_left else windows[-1]
    if window.data != target.data:
        if open_left:
            await Nvim.exec("wincmd H")
        else:
            await Nvim.exec("wincmd L")
        await resize_fm_windows(last_used=window_order, width=width)


async def _open_fm_window(
    settings: Settings,
    window_order: Mapping[ExtData, None],
    opts: _Args,
    width: int,
) -> None:
    cwin = await Window.get_current()
    win = await anext(find_fm_windows_in_tab(last_used=window_order), None)
    if win:
        if opts.toggle:
            wins = await Window.list()
            if len(wins) > 1:
                await win.close()
        else:
            await Window.set_current(win)
    else:
        buf = await anext(find_fm_buffers(), None)
        if not buf:
            buf = await new_fm_buffer(settings=settings)

        win = await new_window(
            last_used=window_order,
            win_local=settings.win_actual_opts,
            open_left=settings.open_left,
            width=width,
        )
        for key, val in settings.win_local_opts.items():
            await win.opts.set(key, val=val)

        await win.set_buf(buf)

        await _ensure_side_window(
            window=win, settings=settings, window_order=window_order, width=width
        )
        if not opts.focus:
            await Window.set_current(cwin)


@rpc(blocking=False)
async def _open(
    state: State, settings: Settings, args: Sequence[str]
) -> Optional[Stage]:
    """
    Toggle sidebar
    """

    try:
        opts = _parse_args(args)
    except ArgparseError as e:
        await Nvim.write(e, error=True)
        return None
    else:
        if opts.version_ctl:
            if git := which("git"):
                try:
                    cwd = await version_ctl_toplv(git, cwd=state.root.path)
                    new_state = await new_root(
                        state=state, settings=settings, new_cwd=cwd, indices=set()
                    )
                except CalledProcessError:
                    await Nvim.write(LANG("cannot find version ctl root"), error=True)
                    return None
            else:
                await Nvim.write(LANG("cannot find version ctl root"), error=True)
                return None
        else:
            new_state = state

        if opts.path:
            path = (
                opts.path
                if opts.path.is_absolute()
                else await Nvim.getcwd() / opts.path
            )
            if not await exists(path, follow=True):
                await new((path,))
            next_state = (
                await maybe_path_above(new_state, settings=settings, path=path)
                or new_state
            )
            await _open_fm_window(
                settings=settings,
                opts=opts,
                window_order=new_state.window_order,
                width=next_state.width,
            )
            await open_file(
                state=state,
                settings=settings,
                path=path,
                click_type=ClickType.primary,
            )
            return Stage(next_state, focus=path)
        else:
            curr = await find_current_buffer_path()
            stage = (
                await new_current_file(state=new_state, settings=settings, current=curr)
                if curr
                else None
            )
            await _open_fm_window(
                settings=settings,
                opts=opts,
                window_order=new_state.window_order,
                width=new_state.width,
            )
            return (
                Stage(stage.state, focus=curr)
                if stage
                else Stage(new_state, focus=curr)
            )
