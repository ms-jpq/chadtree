from typing import Optional

from pynvim import Nvim
from pynvim.api.common import NvimError

from ..nvim.quickfix import quickfix
from ..nvim.wm import find_current_buffer_name
from ..registry import autocmd, rpc
from ..settings.types import Settings
from ..state.next import forward
from ..state.ops import dump_session
from ..state.types import State
from .shared.current import current, new_cwd
from .shared.refresh import refresh
from .types import Stage


@rpc(blocking=False)
def _schedule_update(nvim: Nvim, state: State, settings: Settings) -> Optional[Stage]:
    try:
        return refresh(nvim, state=state, settings=settings, write_out=False)
    except NvimError:
        return None


autocmd("BufWritePost", "FocusGained") << f"lua {_schedule_update.name}()"


@rpc(blocking=False, name="CHADrefocus")
def c_changedir(nvim: Nvim, state: State, settings: Settings, is_visual: bool) -> Stage:
    """
    Follow cwd update
    """

    cwd: str = nvim.funcs.getcwd()
    return new_cwd(nvim, state=state, settings=settings, new_cwd=cwd)


autocmd("DirChanged") << f"lua {c_changedir.name}()"


@rpc(blocking=False)
def a_follow(nvim: Nvim, state: State, settings: Settings) -> Optional[Stage]:
    """
    Follow buffer
    """

    curr = find_current_buffer_name(nvim)
    if curr:
        return current(nvim, state=state, settings=settings, current=curr)
    else:
        return None


autocmd("BufEnter") << f"lua {a_follow.name}()"


@rpc(blocking=False)
def a_session(nvim: Nvim, state: State, settings: Settings) -> None:
    """
    Save CHADTree state
    """

    dump_session(state)


autocmd("FocusLost", "ExitPre") << f"lua {a_session.name}()"


@rpc(blocking=False)
def a_quickfix(nvim: Nvim, state: State, settings: Settings) -> Stage:
    """
    Update quickfix list
    """

    qf = quickfix(nvim)
    new_state = forward(state, settings=settings, qf=qf)
    return Stage(new_state)


autocmd("QuickfixCmdPost") << f"lua {a_quickfix.name}()"
