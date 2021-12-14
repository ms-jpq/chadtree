from typing import Optional

from pynvim import Nvim
from pynvim.api.common import NvimError

from ..registry import rpc
from ..settings.types import Settings
from ..state.types import State
from .shared.refresh import refresh
from .types import Stage


@rpc(blocking=False)
def schedule_update(nvim: Nvim, state: State, settings: Settings) -> Optional[Stage]:
    try:
        stage = refresh(nvim, state=state, settings=settings)
        return stage
    except NvimError:
        return None
