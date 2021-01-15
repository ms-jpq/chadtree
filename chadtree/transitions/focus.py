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
from .shared.current import new_cwd
from .shared.index import indices
from .types import Stage


@rpc(blocking=False)
def _refocus(nvim: Nvim, state: State, settings: Settings, is_visual: bool) -> Stage:
    """
    Follow cwd update
    """

    cwd = get_cwd(nvim)
    return new_cwd(nvim, state=state, settings=settings, new_cwd=cwd)


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
        stage = new_cwd(nvim, state=state, settings=settings, new_cwd=cwd)
        _new_cwd = stage.state.root.path
        write(nvim, LANG("new cwd", cwd=_new_cwd))
        return stage


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
        return new_cwd(nvim, state=state, settings=settings, new_cwd=new_base)


@rpc(blocking=False)
def _change_focus_up(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    Refocus root directory up
    """

    c_root = state.root.path
    parent = dirname(c_root)
    if parent and parent != c_root:
        return None
    else:
        return new_cwd(nvim, state=state, settings=settings, new_cwd=parent)
