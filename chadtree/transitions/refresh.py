from contextlib import contextmanager
from typing import Iterator

from pynvim import Nvim
from pynvim_pp.lib import write

from ..registry import rpc
from ..settings.localization import LANG
from ..settings.types import Settings
from ..state.types import State
from .shared.refresh import refresh as _refresh
from .types import Stage


@contextmanager
def with_manual(nvim: Nvim) -> Iterator[None]:
    write(nvim, LANG("hourglass"))
    yield None
    write(nvim, LANG("ok_sym"))


@rpc(blocking=False)
def refresh(nvim: Nvim, state: State, settings: Settings, is_visual: bool) -> Stage:
    with with_manual(nvim):
        return _refresh(nvim, state=state, settings=settings)
