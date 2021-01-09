from typing import Optional

from pynvim import Nvim

from ..registry import rpc
from ..settings.types import Settings
from ..state.types import State
from .shared.current import current
from .types import Stage


@rpc(blocking=False, name="CHADjump_to_current")
def c_jump_to_current(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    Jump to active file
    """

    curr = state.current
    if curr:
        stage = current(nvim, state=state, settings=settings, current=curr)
        if stage:
            return Stage(state=stage.state, focus=curr)
        else:
            return None
    else:
        return None
