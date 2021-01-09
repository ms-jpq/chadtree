from pynvim import Nvim

from ..registry import rpc
from ..settings.types import Settings
from ..state.types import State
from .shared.refresh import refresh
from .types import Stage


@rpc(blocking=False)
def _refresh(nvim: Nvim, state: State, settings: Settings, is_visual: bool) -> Stage:
    return refresh(nvim, state=state, settings=settings, write_out=True)
