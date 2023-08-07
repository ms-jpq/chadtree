from itertools import chain
from typing import Optional

from pynvim_pp.nvim import Nvim
from pynvim_pp.rpc_types import NvimError
from pynvim_pp.window import Window

from ..fs.ops import is_file
from ..nvim.markers import markers
from ..registry import NAMESPACE, autocmd, rpc
from ..state.next import forward
from ..state.ops import dump_session
from ..state.types import State
from .shared.current import new_current_file, new_root
from .shared.wm import find_current_buffer_path
from .types import Stage


@rpc(blocking=False)
async def save_session(state: State) -> Stage:
    """
    Save CHADTree state
    """

    await dump_session(state)
    new_state = await forward(state, vim_focus=False)
    return Stage(new_state)


_ = autocmd("FocusLost", "ExitPre") << f"lua {NAMESPACE}.{save_session.method}()"


@rpc(blocking=False)
async def _focus_gained(state: State) -> Stage:
    """ """

    new_state = await forward(state, vim_focus=True)
    return Stage(new_state)


_ = autocmd("FocusGained") << f"lua {NAMESPACE}.{_focus_gained.method}()"


@rpc(blocking=False)
async def _record_win_pos(state: State) -> Stage:
    """
    Record last windows
    """

    win = await Window.get_current()
    win_id = win.data

    window_order = {
        wid: None
        for wid in chain(
            (wid for wid in state.window_order if wid != win_id), (win_id,)
        )
    }
    new_state = await forward(state, window_order=window_order)
    return Stage(new_state)


_ = autocmd("WinEnter") << f"lua {NAMESPACE}.{_record_win_pos.method}()"


@rpc(blocking=False)
async def _changedir(state: State) -> Stage:
    """
    Follow cwd update
    """

    cwd = await Nvim.getcwd()
    new_state = await new_root(state, new_cwd=cwd, indices=frozenset())
    return Stage(new_state)


_ = autocmd("DirChanged") << f"lua {NAMESPACE}.{_changedir.method}()"


@rpc(blocking=False)
async def _update_follow(state: State) -> Optional[Stage]:
    """
    Follow buffer
    """

    try:
        if (
            (current := await find_current_buffer_path())
            and await is_file(current)
            and state.current != current
        ):
            stage = await new_current_file(state, current=current)
            return stage
        else:
            return None
    except NvimError:
        return None


_ = autocmd("BufEnter") << f"lua {NAMESPACE}.{_update_follow.method}()"


@rpc(blocking=False)
async def _update_markers(state: State) -> Stage:
    """
    Update markers
    """

    mks = await markers()
    new_state = await forward(state, markers=mks)
    return Stage(new_state)


_ = autocmd("QuickfixCmdPost") << f"lua {NAMESPACE}.{_update_markers.method}()"
