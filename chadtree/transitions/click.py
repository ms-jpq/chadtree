from typing import Optional

from pynvim_pp.nvim import Nvim
from std2 import anext

from ..fs.cartographer import is_dir
from ..fs.types import Mode
from ..registry import rpc
from ..settings.localization import LANG
from ..settings.types import Settings
from ..state.next import forward
from ..state.types import State
from .shared.index import indices
from .shared.open_file import open_file
from .shared.wm import find_fm_windows
from .types import ClickType, Stage


async def _click(
    state: State, settings: Settings, is_visual: bool, click_type: ClickType
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
                    paths = {node.path}
                    index = state.index ^ paths
                    new_state = await forward(
                        state, settings=settings, index=index, paths=paths
                    )
                    return Stage(new_state)
            else:
                nxt = await open_file(
                    state,
                    settings=settings,
                    path=node.path,
                    click_type=click_type,
                )

                if settings.close_on_open and click_type != ClickType.secondary:
                    async for win, _ in find_fm_windows():
                        await win.close()

                return nxt


@rpc(blocking=False)
async def _primary(
    state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    Folders -> toggle
    File -> open
    """

    return await _click(
        state,
        settings=settings,
        is_visual=is_visual,
        click_type=ClickType.primary,
    )


@rpc(blocking=False)
async def _secondary(
    state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    Folders -> toggle
    File -> preview
    """

    return await _click(
        state,
        settings=settings,
        is_visual=is_visual,
        click_type=ClickType.secondary,
    )


@rpc(blocking=False)
async def _tertiary(
    state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    Folders -> toggle
    File -> open in new tab
    """

    return await _click(
        state,
        settings=settings,
        is_visual=is_visual,
        click_type=ClickType.tertiary,
    )


@rpc(blocking=False)
async def _v_split(
    state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    Folders -> toggle
    File -> open in vertical split
    """

    return await _click(
        state,
        settings=settings,
        is_visual=is_visual,
        click_type=ClickType.v_split,
    )


@rpc(blocking=False)
async def _h_split(
    state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    Folders -> toggle
    File -> open in horizontal split
    """

    return await _click(
        state, settings=settings, is_visual=is_visual, click_type=ClickType.h_split
    )
