from typing import Any

from ..registry import rpc
from ..state.types import State


@rpc(blocking=False)
async def _noop(state: State, *_: Any) -> None:
    """
    NOOP
    """
