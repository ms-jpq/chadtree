from os.path import normcase, normpath
from typing import Optional

from pynvim_pp.nvim import Nvim
from std2 import anext

from ..fs.cartographer import is_dir
from ..registry import rpc
from ..settings.localization import LANG
from ..settings.types import Settings
from ..state.types import State
from .shared.current import new_current_file, new_root
from .shared.index import indices
from .types import Stage


@rpc(blocking=False)
async def _jump_to_current(
    state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    Jump to active file
    """

    if not (curr := state.current):
        return None
    else:
        stage = await new_current_file(state, settings=settings, current=curr)
        if not stage:
            return None
        else:
            return Stage(state=stage.state, focus=curr)


@rpc(blocking=False)
async def _refocus(state: State, settings: Settings, is_visual: bool) -> Stage:
    """
    Follow cwd update
    """

    cwd = await Nvim.getcwd()
    new_state = await new_root(state, settings=settings, new_cwd=cwd, indices=set())
    focus = new_state.root.path
    return Stage(new_state, focus=focus)


@rpc(blocking=False)
async def _change_dir(
    state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    Change root directory
    """

    node = await anext(indices(state, is_visual=is_visual), None)
    if not node:
        return None
    else:
        cwd = node.path if is_dir(node) else node.path.parent
        new_state = await new_root(state, settings=settings, new_cwd=cwd, indices=set())
        escaped = await Nvim.fn.fnameescape(str, normcase(new_state.root.path))
        await Nvim.exec(f"chdir {escaped}")
        await Nvim.write(LANG("new cwd", cwd=normpath(new_state.root.path)))
        return Stage(new_state, focus=new_state.root.path)


@rpc(blocking=False)
async def _change_focus(
    state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    Refocus root directory
    """

    node = await anext(indices(state, is_visual=is_visual), None)
    if not node:
        return None
    else:
        new_base = node.path if is_dir(node) else node.path.parent
        new_state = await new_root(
            state, settings=settings, new_cwd=new_base, indices=set()
        )
        focus = node.path
        return Stage(new_state, focus=focus)


@rpc(blocking=False)
async def _change_focus_up(
    state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    Refocus root directory up
    """

    node = await anext(indices(state, is_visual=is_visual), None)
    if not node:
        return None
    else:
        new_state = await new_root(
            state,
            settings=settings,
            new_cwd=state.root.path.parent,
            indices=set(),
        )
        return Stage(new_state, focus=node.path)
