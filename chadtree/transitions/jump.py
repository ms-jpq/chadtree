from typing import Optional

from pynvim import Nvim

from ..registry import rpc
from ..settings.types import Settings
from ..state.types import State
from .shared.current import current
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
        stage = current(nvim, state=state, settings=settings, current=curr)
        if not stage:
            return None
        else:
            return Stage(state=stage.state, focus=curr)
