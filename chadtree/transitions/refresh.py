from pynvim import Nvim

from ..registry import rpc
from ..settings.types import Settings
from ..state.types import State
from .shared.refresh import refresh as _refresh
from .shared.refresh import with_manual
from .types import Stage


@rpc(blocking=False)
def refresh(nvim: Nvim, state: State, settings: Settings, is_visual: bool) -> Stage:
    with with_manual(nvim):
        return _refresh(nvim, state=state, settings=settings)
