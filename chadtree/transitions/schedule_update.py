from asyncio import gather
from typing import Optional

from pynvim_pp.nvim import Nvim
from pynvim_pp.rpc_types import NvimError
from std2.asyncio import pure

from ..lsp.diagnostics import poll
from ..registry import rpc
from ..state.next import forward
from ..state.ops import dump_session
from ..state.types import State
from ..version_ctl.git import status
from ..version_ctl.types import VCStatus
from .shared.refresh import refresh
from .types import Stage


@rpc(blocking=False)
async def scheduled_update(state: State, init: bool = False) -> Optional[Stage]:
    cwd = await Nvim.getcwd()
    store = dump_session(state) if state.vim_focus else pure(None)

    try:
        stage, diagnostics, vc, _ = await gather(
            refresh(state=state),
            poll(state.settings.min_diagnostics_severity),
            status(cwd, prev=state.vc)
            if not init and state.enable_vc
            else pure(VCStatus()),
            store,
        )
    except NvimError:
        return None
    else:
        new_state = await forward(stage.state, diagnostics=diagnostics, vc=vc)
        return Stage(new_state, focus=stage.focus)
