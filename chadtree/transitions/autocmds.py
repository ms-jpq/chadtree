from typing import Optional

from pynvim import Nvim
from pynvim.api.common import NvimError
from pynvim_pp.api import get_cwd, win_close
from pynvim_pp.float_win import list_floatwins

from ..nvim.quickfix import quickfix
from ..registry import autocmd, rpc
from ..settings.types import Settings
from ..state.next import forward
from ..state.ops import dump_session
from ..state.types import State
from .shared.current import new_current_file, new_root
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
def save_session(nvim: Nvim, state: State, settings: Settings) -> None:
    """
    Save CHADTree state
    """

    dump_session(state)


autocmd("FocusLost", "ExitPre") << f"lua {save_session.name}()"


@rpc(blocking=False)
def _kill_float_wins(nvim: Nvim, state: State, settings: Settings) -> None:
    wins = tuple(list_floatwins(nvim))
    if len(wins) != 2:
        for win in wins:
            win_close(nvim, win=win)


autocmd("WinClosed") << f"lua {_kill_float_wins.name}()"


@rpc(blocking=False)
def _changedir(nvim: Nvim, state: State, settings: Settings) -> Stage:
    """
    Follow cwd update
    """

    cwd = get_cwd(nvim)
    new_state = new_root(nvim, state=state, settings=settings, new_cwd=cwd)
    return Stage(new_state)


autocmd("DirChanged") << f"lua {_changedir.name}()"


@rpc(blocking=False)
def _update_follow(nvim: Nvim, state: State, settings: Settings) -> Optional[Stage]:
    """
    Follow buffer
    """

    curr = find_current_buffer_name(nvim)
    if curr:
        return new_current_file(nvim, state=state, settings=settings, current=curr)
    else:
        return None


autocmd("BufEnter") << f"lua {_update_follow.name}()"


@rpc(blocking=False)
def _update_quickfix(nvim: Nvim, state: State, settings: Settings) -> Stage:
    """
    Update quickfix list
    """

    qf = quickfix(nvim)
    new_state = forward(state, settings=settings, qf=qf)
    return Stage(new_state)


autocmd("QuickfixCmdPost") << f"lua {_update_quickfix.name}()"
