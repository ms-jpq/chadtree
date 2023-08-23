from typing import Optional, Union

from pynvim_pp.nvim import Nvim
from std2 import anext
from std2.types import Void, VoidType

from ..registry import rpc
from ..settings.localization import LANG
from ..state.next import forward
from ..state.types import Selection, State
from ..version_ctl.types import VCStatus
from .shared.index import indices
from .types import Stage


@rpc(blocking=False)
async def _toggle_hidden(state: State, is_visual: bool) -> Optional[Stage]:
    """
    Toggle hidden
    """

    node = await anext(indices(state, is_visual=is_visual))
    if not node:
        return None
    else:
        focus = node.path
        show_hidden = not state.show_hidden
        selection: Selection = state.selection if show_hidden else frozenset()
        new_state = await forward(state, show_hidden=show_hidden, selection=selection)
        return Stage(new_state, focus=focus)


@rpc(blocking=False)
async def _toggle_follow(state: State, is_visual: bool) -> Stage:
    """
    Toggle follow
    """

    new_state = await forward(state, follow=not state.follow)
    await Nvim.write(LANG("follow_mode_indi", follow=str(new_state.follow)))
    return Stage(new_state)


@rpc(blocking=False)
async def _toggle_follow_links(state: State, is_visual: bool) -> Stage:
    """
    Toggle --follow
    """

    follow_links = not state.follow_links
    new_state = await forward(state, follow_links=follow_links)
    await Nvim.write(LANG("follow_links_indi", follow=str(new_state.follow_links)))
    return Stage(new_state)


@rpc(blocking=False)
async def _toggle_version_control(state: State, is_visual: bool) -> Stage:
    """
    Toggle version control
    """

    enable_vc = not state.enable_vc
    vc: Union[VoidType, VCStatus] = Void if enable_vc else VCStatus()
    new_state = await forward(state, enable_vc=enable_vc, vc=vc)
    await Nvim.write(LANG("version_control_indi", enable_vc=str(new_state.enable_vc)))
    return Stage(new_state)
