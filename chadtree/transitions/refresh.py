from pynvim import Nvim

from ..registry import rpc
from ..settings.types import Settings
from ..state.types import State
from .shared.refresh import refresh as _refresh
from .types import Stage


@rpc(blocking=False)
def refresh(nvim: Nvim, state: State, settings: Settings, is_visual: bool) -> Stage:
    return _refresh(nvim, state=state, settings=settings, manual=True)
