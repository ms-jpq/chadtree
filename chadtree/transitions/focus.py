from os.path import dirname
from typing import Optional

from pynvim import Nvim
from pynvim_pp.api import get_cwd
from pynvim_pp.lib import write

from ..fs.cartographer import is_dir
from ..registry import rpc
from ..settings.localization import LANG
from ..settings.types import Settings
from ..state.types import State
from .shared.current import new_current_file, new_root
from .shared.index import indices
from .types import Stage


@rpc(blocking=False)
def _jump_to_current(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    Jump to active file
    """

    curr = state.current
    if not curr:
        return None
    else:
        stage = new_current_file(nvim, state=state, settings=settings, current=curr)
        if not stage:
            return None
        else:
            return Stage(state=stage.state, focus=curr)


@rpc(blocking=False)
def _refocus(nvim: Nvim, state: State, settings: Settings, is_visual: bool) -> Stage:
    """
    Follow cwd update
    """

    cwd = get_cwd(nvim)
    new_state = new_root(nvim, state=state, settings=settings, new_cwd=cwd)
    focus = new_state.root.path
    return Stage(new_state, focus=focus)


@rpc(blocking=False)
def _change_dir(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    Change root directory
    """

    node = next(indices(nvim, state=state, is_visual=is_visual), None)
    if not node:
        return None
    else:
        cwd = node.path if is_dir(node) else dirname(node.path)
        new_state = new_root(nvim, state=state, settings=settings, new_cwd=cwd)
        focus = new_state.root.path
        nvim.command(f"chdir {focus}")
        write(nvim, LANG("new cwd", cwd=focus))
        return Stage(new_state, focus=focus)


@rpc(blocking=False)
def _change_focus(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    Refocus root directory
    """

    node = next(indices(nvim, state=state, is_visual=is_visual), None)
    if not node:
        return None
    else:
        new_base = node.path if is_dir(node) else dirname(node.path)
        new_state = new_root(nvim, state=state, settings=settings, new_cwd=new_base)
        focus = new_state.root.path
        return Stage(new_state, focus=focus)


@rpc(blocking=False)
def _change_focus_up(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Stage:
    """
    Refocus root directory up
    """

    root = state.root.path
    parent = dirname(root)
    new_state = new_root(nvim, state=state, settings=settings, new_cwd=parent)
    focus = new_state.root.path
    return Stage(new_state, focus=focus)
