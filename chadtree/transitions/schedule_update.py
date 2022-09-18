from typing import Optional

from pynvim_pp.types import NvimError

from ..registry import rpc
from ..settings.types import Settings
from ..state.types import State
from .shared.refresh import refresh
from .types import Stage


@rpc(blocking=False)
async def scheduled_update(state: State, settings: Settings) -> Optional[Stage]:
    try:
        stage = await refresh(state=state, settings=settings)
    except NvimError:
        return None
    else:
        return stage
