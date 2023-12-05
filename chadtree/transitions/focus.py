from os.path import normcase, normpath
from pathlib import PurePath
from typing import Optional

from pynvim_pp.nvim import Nvim
from std2 import anext

from ..fs.cartographer import act_like_dir
from ..fs.ops import ancestors
from ..registry import rpc
from ..settings.localization import LANG
from ..state.types import State
from .shared.current import maybe_path_above, new_current_file, new_root
from .shared.index import indices
from .types import Stage


async def _jump(state: State, path: PurePath) -> Optional[Stage]:
    if new_state := await maybe_path_above(state, paths={path}):
        return Stage(new_state, focus=path)
    elif stage := await new_current_file(state, current=path):
        return Stage(stage.state, focus=path)
    else:
        return None


@rpc(blocking=False)
async def _jump_to_current(state: State, is_visual: bool) -> Optional[Stage]:
    """
    Jump to active file
    """

    if not (curr := state.current):
        return None
    else:
        return await _jump(state, path=curr)


@rpc(blocking=False)
async def _refocus(state: State, is_visual: bool) -> Stage:
    """
    Follow cwd update
    """

    cwd = await Nvim.getcwd()
    new_state = await new_root(state, new_cwd=cwd, indices=frozenset())
    focus = new_state.root.path
    return Stage(new_state, focus=focus)


@rpc(blocking=False)
async def _change_dir(state: State, is_visual: bool) -> Optional[Stage]:
    """
    Change root directory
    """

    node = await anext(indices(state, is_visual=is_visual), None)
    if not node:
        return None
    else:
        cwd = (
            node.path
            if act_like_dir(node, follow_links=state.follow_links)
            else node.path.parent
        )
        new_state = await new_root(state, new_cwd=cwd, indices=frozenset())
        escaped = await Nvim.fn.fnameescape(str, normcase(new_state.root.path))
        await Nvim.exec(f"chdir {escaped}")
        await Nvim.write(LANG("new cwd", cwd=normpath(new_state.root.path)))
        return Stage(new_state, focus=new_state.root.path)


@rpc(blocking=False)
async def _change_focus(state: State, is_visual: bool) -> Optional[Stage]:
    """
    Refocus root directory
    """

    node = await anext(indices(state, is_visual=is_visual), None)
    if not node:
        return None
    else:
        new_base = (
            node.path
            if act_like_dir(node, follow_links=state.follow_links)
            else node.path.parent
        )
        new_state = await new_root(state, new_cwd=new_base, indices=frozenset())
        focus = node.path
        return Stage(new_state, focus=focus)


@rpc(blocking=False)
async def _change_focus_up(state: State, is_visual: bool) -> Optional[Stage]:
    """
    Refocus root directory up
    """

    node = await anext(indices(state, is_visual=is_visual), None)
    if not node:
        return None
    else:
        new_state = await new_root(
            state, new_cwd=state.root.path.parent, indices=frozenset()
        )
        return Stage(new_state, focus=node.path)
