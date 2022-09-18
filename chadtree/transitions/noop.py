from typing import Any

from ..registry import rpc
from ..settings.types import Settings
from ..state.types import State


@rpc(blocking=False)
async def _noop(state: State, settings: Settings, *_: Any) -> None:
    """
    NOOP
    """
