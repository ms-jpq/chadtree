from asyncio import gather
from typing import Optional

from pynvim_pp.nvim import Nvim
from pynvim_pp.types import NvimError
from std2.asyncio import pure

from ..registry import rpc
from ..settings.types import Settings
from ..state.next import forward
from ..state.ops import dump_session
from ..state.types import State
from ..version_ctl.git import status
from ..version_ctl.types import VCStatus
from .shared.refresh import refresh
from .types import Stage


@rpc(blocking=False)
async def scheduled_update(state: State, settings: Settings) -> Optional[Stage]:
    cwd = await Nvim.getcwd()

    try:
        stage, vc, session = await gather(
            refresh(state=state, settings=settings),
            status(cwd) if state.enable_vc else pure(VCStatus()),
            dump_session(state),
        )
    except NvimError:
        return None
    else:
        new_state = await forward(
            stage.state, settings=settings, vc=vc, session=session
        )
        return Stage(new_state, focus=stage.focus)
