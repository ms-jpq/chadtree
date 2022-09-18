from typing import Optional

from pynvim_pp.nvim import Nvim

from ..registry import rpc
from ..settings.types import Settings
from ..state.next import forward
from ..state.types import State
from ..version_ctl.git import status
from .types import Stage


@rpc(blocking=False)
async def vc_refresh(state: State, settings: Settings) -> Optional[Stage]:
    """
    VC Refresh
    """

    if state.enable_vc:
        cwd = await Nvim.getcwd()
        vc = await status(cwd)
        new_state = await forward(state, settings=settings, vc=vc)
        return Stage(new_state)
    else:
        return None
