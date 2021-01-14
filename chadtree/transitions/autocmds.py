from typing import Optional

from pynvim import Nvim
from pynvim.api.common import NvimError

from ..nvim.quickfix import quickfix
from ..registry import autocmd, rpc
from ..settings.types import Settings
from ..state.next import forward
from ..state.ops import dump_session
from ..state.types import State
from .shared.current import current, new_cwd
from .shared.refresh import refresh
from .shared.wm import find_current_buffer_name
from .types import Stage


@rpc(blocking=False)
def schedule_update(nvim: Nvim, state: State, settings: Settings) -> Optional[Stage]:
    try:
        return refresh(nvim, state=state, settings=settings, write_out=False)
    except NvimError:
        return None


autocmd("BufWritePost", "FocusGained") << f"lua {schedule_update.name}()"


@rpc(blocking=False)
def _changedir(nvim: Nvim, state: State, settings: Settings) -> Stage:
    """
    Follow cwd update
    """

    cwd: str = nvim.funcs.getcwd()
    return new_cwd(nvim, state=state, settings=settings, new_cwd=cwd)


autocmd("DirChanged") << f"lua {_changedir.name}()"


@rpc(blocking=False)
def _update_follow(nvim: Nvim, state: State, settings: Settings) -> Optional[Stage]:
    """
    Follow buffer
    """

    curr = find_current_buffer_name(nvim)
    if curr:
        return current(nvim, state=state, settings=settings, current=curr)
    else:
        return None


autocmd("BufEnter") << f"lua {_update_follow.name}()"


@rpc(blocking=True)
def _dump_session(nvim: Nvim, state: State, settings: Settings) -> None:
    """
    Save CHADTree state
    """

    dump_session(state)


autocmd("FocusLost", "ExitPre") << f"lua {_dump_session.name}()"


@rpc(blocking=False)
def _update_quickfix(nvim: Nvim, state: State, settings: Settings) -> Stage:
    """
    Update quickfix list
    """

    qf = quickfix(nvim)
    new_state = forward(state, settings=settings, qf=qf)
    return Stage(new_state)


autocmd("QuickfixCmdPost") << f"lua {_update_quickfix.name}()"
