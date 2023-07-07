from typing import Optional

from pynvim_pp.nvim import Nvim
from std2 import anext

from ..fs.cartographer import is_dir
from ..fs.types import Mode
from ..registry import rpc
from ..settings.localization import LANG
from ..state.next import forward
from ..state.types import State
from .shared.index import indices
from .shared.open_file import open_file
from .shared.wm import find_fm_windows
from .types import ClickType, Stage


async def _click(
    state: State, is_visual: bool, click_type: ClickType
) -> Optional[Stage]:
    node = await anext(indices(state, is_visual=is_visual), None)

    if not node:
        return None
    else:
        if Mode.orphan_link in node.mode:
            await Nvim.write(LANG("dead_link", name=node.path.name), error=True)
            return None
        else:
            if is_dir(node):
                if node.path == state.root.path:
                    return None
                elif state.filter_pattern:
                    await Nvim.write(LANG("filter_click"))
                    return None
                else:
                    index = state.index ^ {node.path}
                    invalidate_dirs = {node.path}
                    new_state = await forward(
                        state,
                        index=index,
                        invalidate_dirs=invalidate_dirs,
                    )
                    return Stage(new_state)
            else:
                nxt = await open_file(
                    state,
                    path=node.path,
                    click_type=click_type,
                )

                if state.settings.close_on_open and click_type != ClickType.secondary:
                    async for win, _ in find_fm_windows():
                        await win.close()

                return nxt


@rpc(blocking=False)
async def _primary(state: State, is_visual: bool) -> Optional[Stage]:
    """
    Folders -> toggle
    File -> open
    """

    return await _click(state, is_visual=is_visual, click_type=ClickType.primary)


@rpc(blocking=False)
async def _secondary(state: State, is_visual: bool) -> Optional[Stage]:
    """
    Folders -> toggle
    File -> preview
    """

    return await _click(state, is_visual=is_visual, click_type=ClickType.secondary)


@rpc(blocking=False)
async def _tertiary(state: State, is_visual: bool) -> Optional[Stage]:
    """
    Folders -> toggle
    File -> open in new tab
    """

    return await _click(state, is_visual=is_visual, click_type=ClickType.tertiary)


@rpc(blocking=False)
async def _v_split(state: State, is_visual: bool) -> Optional[Stage]:
    """
    Folders -> toggle
    File -> open in vertical split
    """

    return await _click(state, is_visual=is_visual, click_type=ClickType.v_split)


@rpc(blocking=False)
async def _h_split(state: State, is_visual: bool) -> Optional[Stage]:
    """
    Folders -> toggle
    File -> open in horizontal split
    """

    return await _click(state, is_visual=is_visual, click_type=ClickType.h_split)
