from typing import Any

from pynvim import Nvim

from ..registry import rpc
from ..settings.types import Settings
from ..state.types import State


@rpc(blocking=False)
def _noop(nvim: Nvim, state: State, settings: Settings, *_: Any) -> None:
    """
    NOOP
    """
