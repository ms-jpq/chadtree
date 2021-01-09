from typing import Optional

from pynvim import Nvim
from pynvim.api.common import NvimError

from ..registry import autocmd, rpc
from ..settings.types import Settings
from ..state.types import State
from .refresh import refresh
from .types import Stage


@rpc(blocking=False)
def _schedule_update(nvim: Nvim, state: State, settings: Settings) -> Optional[Stage]:
    try:
        return refresh(nvim, state=state, settings=settings, write_out=False)
    except NvimError:
        return None


autocmd("BufWritePost", "FocusGained") << f"lua {_schedule_update.name}()"
