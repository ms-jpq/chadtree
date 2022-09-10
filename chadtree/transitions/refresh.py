from contextlib import asynccontextmanager
from typing import AsyncIterator

from pynvim_pp.nvim import Nvim

from ..registry import rpc
from ..settings.localization import LANG
from ..settings.types import Settings
from ..state.types import State
from .shared.refresh import refresh as _refresh
from .types import Stage


@asynccontextmanager
async def with_manual() -> AsyncIterator[None]:
    await Nvim.write(LANG("hourglass"))
    yield None
    await Nvim.write(LANG("ok_sym"))


@rpc(blocking=False)
async def refresh(state: State, settings: Settings, is_visual: bool) -> Stage:
    async with with_manual():
        return await _refresh(state, settings=settings)
