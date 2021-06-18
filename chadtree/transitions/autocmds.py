from os import chdir
from os.path import isfile
from pathlib import PurePath
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
from .shared.wm import find_current_buffer_name
from .types import Stage


@rpc(blocking=False)
def save_session(nvim: Nvim, state: State, settings: Settings) -> None:
    """
    Save CHADTree state
    """

    dump_session(state, use_xdg=settings.xdg)


autocmd("FocusLost", "ExitPre") << f"lua {save_session.name}()"


@rpc(blocking=False)
def _kill_float_wins(nvim: Nvim, state: State, settings: Settings) -> None:
    try:
        wins = tuple(list_floatwins(nvim))
        if len(wins) != 2:
            for win in wins:
                win_close(nvim, win=win)
    except NvimError:
        pass


autocmd("WinEnter") << f"lua {_kill_float_wins.name}()"


@rpc(blocking=False)
def _changedir(nvim: Nvim, state: State, settings: Settings) -> Stage:
    """
    Follow cwd update
    """

    cwd = PurePath(get_cwd(nvim))
    chdir(cwd)
    new_state = new_root(
        nvim, state=state, settings=settings, new_cwd=cwd, indices=set()
    )
    return Stage(new_state)


autocmd("DirChanged") << f"lua {_changedir.name}()"


@rpc(blocking=False)
def _update_follow(nvim: Nvim, state: State, settings: Settings) -> Optional[Stage]:
    """
    Follow buffer
    """

    try:
        curr = find_current_buffer_name(nvim)
        if isfile(curr):
            stage = new_current_file(nvim, state=state, settings=settings, current=curr)
            return Stage(state=stage.state, focus=stage.focus) if stage else None
        else:
            return None
    except NvimError:
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

