from typing import Union

from pynvim import Nvim
from pynvim_pp.lib import write
from std2.types import Void, VoidType

from ..registry import rpc
from ..settings.localization import LANG
from ..settings.types import Settings
from ..state.next import forward
from ..state.types import Selection, State
from ..version_ctl.types import VCStatus
from .types import Stage


@rpc(blocking=False)
def _toggle_hidden(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Stage:
    """
    Toggle hidden
    """

    show_hidden = not state.show_hidden
    selection: Selection = state.selection if show_hidden else set()
    new_state = forward(
        state, settings=settings, show_hidden=show_hidden, selection=selection
    )
    return Stage(new_state)


@rpc(blocking=False)
def _toggle_follow(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Stage:
    """
    Toggle follow
    """

    new_state = forward(state, settings=settings, follow=not state.follow)
    write(nvim, LANG("follow_mode_indi", follow=str(new_state.follow)))
    return Stage(new_state)


@rpc(blocking=False)
def _toggle_version_control(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Stage:
    """
    Toggle version control
    """

    enable_vc = not state.enable_vc
    vc: Union[VoidType, VCStatus] = Void if enable_vc else VCStatus()
    new_state = forward(state, settings=settings, enable_vc=enable_vc, vc=vc)
    write(nvim, LANG("version_control_indi", enable_vc=str(new_state.enable_vc)))
    return Stage(new_state)
