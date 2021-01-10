from os.path import dirname
from typing import Optional

from pynvim import Nvim

from ..fs.cartographer import is_dir
from ..registry import rpc
from ..settings.types import Settings
from ..state.types import State
from .shared.current import new_cwd
from .shared.index import indices
from .types import Stage


@rpc(blocking=False, name="CHADchange_focus")
def c_change_focus(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    Refocus root directory
    """

    node = next(indices(nvim, state=state, is_visual=is_visual), None)
    if node:
        new_base = node.path if is_dir(node) else dirname(node.path)
        return new_cwd(nvim, state=state, settings=settings, new_cwd=new_base)
    else:
        return None


@rpc(blocking=False, name="CHADchange_focus_up")
def c_change_focus_up(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    Refocus root directory up
    """

    c_root = state.root.path
    parent = dirname(c_root)
    if parent and parent != c_root:
        return new_cwd(nvim, state=state, settings=settings, new_cwd=parent)
    else:
        return None
