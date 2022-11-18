from asyncio import Lock, gather
from functools import lru_cache
from typing import Optional

from pynvim_pp.nvim import Nvim
from pynvim_pp.types import NvimError

from ..registry import rpc
from ..settings.types import Settings
from ..state.next import forward
from ..state.ops import dump_session
from ..state.types import State
from ..version_ctl.git import status
from .shared.refresh import refresh
from .types import Stage


@lru_cache(maxsize=None)
def _lock() -> Lock:
    return Lock()


@rpc(blocking=False)
async def scheduled_update(state: State, settings: Settings) -> Optional[Stage]:
    async with _lock():
        cwd = await Nvim.getcwd()

        try:
            stage, vc, _ = await gather(
                refresh(state=state, settings=settings),
                status(cwd),
                dump_session(state, session_store=state.session_store),
            )
        except NvimError:
            return None
        else:
            new_state = await forward(stage.state, settings=settings, vc=vc)
            return Stage(new_state, focus=stage.focus)
