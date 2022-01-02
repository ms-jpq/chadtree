from typing import Optional

from pynvim import Nvim
from pynvim.api.common import NvimError
from pynvim_pp.api import get_cwd

from ..fs.ops import is_file
from ..nvim.markers import markers
from ..registry import NAMESPACE, autocmd, rpc
from ..settings.types import Settings
from ..state.next import forward
from ..state.ops import dump_session
from ..state.types import State
from .shared.current import new_current_file, new_root
from .shared.wm import find_current_buffer_path
from .types import Stage


@rpc(blocking=False)
def save_session(nvim: Nvim, state: State, settings: Settings) -> None:
    """
    Save CHADTree state
    """

    dump_session(state, session_store=state.session_store)


autocmd("FocusLost", "ExitPre") << f"lua {NAMESPACE}.{save_session.name}()"


@rpc(blocking=False)
def _store_win_pos(nvim: Nvim, state: State, settings: Settings) -> None:
    """
    Store last windows
    """


autocmd("WinEnter") << f"lua {NAMESPACE}.{_store_win_pos.name}()"


@rpc(blocking=False)
def _changedir(nvim: Nvim, state: State, settings: Settings) -> Stage:
    """
    Follow cwd update
    """

    cwd = get_cwd(nvim)
    new_state = new_root(
        nvim, state=state, settings=settings, new_cwd=cwd, indices=set()
    )
    return Stage(new_state)


autocmd("DirChanged") << f"lua {NAMESPACE}.{_changedir.name}()"


@rpc(blocking=False)
def _update_follow(nvim: Nvim, state: State, settings: Settings) -> Optional[Stage]:
    """
    Follow buffer
    """

    try:

        if (curr := find_current_buffer_path(nvim)) and is_file(state.pool, path=curr):
            stage = new_current_file(nvim, state=state, settings=settings, current=curr)
            return stage
        else:
            return None
    except NvimError:
        return None


autocmd("BufEnter") << f"lua {NAMESPACE}.{_update_follow.name}()"


@rpc(blocking=False)
def _update_markers(nvim: Nvim, state: State, settings: Settings) -> Stage:
    """
    Update markers
    """

    mks = markers(nvim)
    new_state = forward(state, settings=settings, markers=mks)
    return Stage(new_state)


autocmd("QuickfixCmdPost") << f"lua {NAMESPACE}.{_update_markers.name}()"
