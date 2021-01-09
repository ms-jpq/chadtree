from typing import Optional

from pynvim import Nvim
from pynvim.api.common import NvimError

from ..fs.cartographer import new
from ..nvim.quickfix import quickfix
from ..nvim.wm import find_current_buffer_name
from ..registry import autocmd, rpc
from ..settings.types import Settings
from ..state.next import forward
from ..state.ops import dump_session
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


def _change_dir(nvim: Nvim, state: State, settings: Settings, new_base: str) -> Stage:
    index = state.index | {new_base}
    root = new(new_base, index=index)
    new_state = forward(state, settings=settings, root=root, index=index)
    return Stage(new_state)


def _refocus(nvim: Nvim, state: State, settings: Settings) -> Stage:
    cwd: str = nvim.funcs.getcwd()
    return _change_dir(nvim, state=state, settings=settings, new_base=cwd)


@rpc(blocking=False, name="CHADrefocus")
def c_changedir(nvim: Nvim, state: State, settings: Settings, is_visual: bool) -> Stage:
    """
    Follow cwd update
    """

    return _refocus(nvim, state=state, settings=settings)


autocmd("DirChanged") << f"lua {c_changedir.name}()"


@rpc(blocking=False)
def a_follow(nvim: Nvim, state: State, settings: Settings) -> Optional[Stage]:
    """
    Follow buffer
    """

    current = find_current_buffer_name(nvim)
    if current:
        return _current(nvim, state=state, settings=settings, current=current)
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
