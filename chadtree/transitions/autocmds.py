from asyncio import Task, create_task, sleep
from collections.abc import Sequence
from itertools import chain
from typing import Optional

from pynvim_pp.buffer import Buffer
from pynvim_pp.nvim import Nvim
from pynvim_pp.rpc_types import NvimError
from pynvim_pp.window import Window
from std2.asyncio import cancel
from std2.cell import RefCell

from ..consts import FM_FILETYPE, URI_SCHEME
from ..fs.ops import ancestors, is_file
from ..lsp.diagnostics import poll
from ..nvim.markers import markers
from ..registry import NAMESPACE, autocmd, rpc
from ..settings.types import Settings
from ..state.next import forward
from ..state.ops import dump_session
from ..state.types import State
from .shared.current import new_current_file, new_root
from .shared.wm import (
    find_current_buffer_path,
    find_fm_buffers,
    is_fm_buf_name,
    is_fm_buffer,
    restore_non_fm_win,
    setup_fm_buf,
)
from .types import Stage

_CELL = RefCell[Optional[Task]](None)


async def _setup_fm_win(settings: Settings, win: Window) -> None:
    for key, val in settings.win_local_opts.items():
        await win.opts.set(key, val=val)


async def setup(settings: Settings) -> None:
    async for buf in find_fm_buffers():
        await setup_fm_buf(settings, buf=buf)
    for win in await Window.list():
        buf = await win.get_buf()
        if await is_fm_buffer(buf):
            await _setup_fm_win(settings, win=win)


@rpc(blocking=False)
async def _when_idle(state: State) -> None:
    if task := _CELL.val:
        _CELL.val = None
        await cancel(task)

    async def cont() -> None:
        await sleep(state.settings.idle_timeout)
        diagnostics = await poll(state.settings.min_diagnostics_severity)
        await forward(state, diagnostics=diagnostics)

    _CELL.val = create_task(cont())


_ = autocmd("CursorHold", "CursorHoldI") << f"lua {NAMESPACE}.{_when_idle.method}()"


@rpc(blocking=False)
async def save_session(state: State) -> Stage:
    """
    Save CHADTree state
    """

    await dump_session(state)
    new_state = await forward(state, vim_focus=False)
    print("save")
    return Stage(new_state)


_ = autocmd("FocusLost", "ExitPre") << f"lua {NAMESPACE}.{save_session.method}()"
_ = (
    autocmd("User", modifiers=("CHADSave",))
    << f"lua {NAMESPACE}.{save_session.method}()"
)


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
async def _restore(state: State, args: Sequence[str]) -> None:
    win = await Window.get_current()
    await restore_non_fm_win(state.settings.win_actual_opts, win=win)


@rpc(blocking=False)
async def _update_follow(state: State) -> Optional[Stage]:
    """
    Follow buffer
    """

    win = await Window.get_current()
    buf = await Buffer.get_current()
    name = await buf.get_name()
    is_fm_win = await win.vars.get(bool, URI_SCHEME)
    is_fm_buf = await buf.filetype() == FM_FILETYPE
    is_fm_uri = name and is_fm_buf_name(name)

    if is_fm_win and not is_fm_buf:
        await restore_non_fm_win(state.settings.win_actual_opts, win=win)

    if is_fm_uri or is_fm_buf and not is_fm_win:
        await _setup_fm_win(state.settings, win=win)

    if is_fm_uri and not is_fm_buf:
        await setup_fm_buf(state.settings, buf=buf)

    try:
        if (current := await find_current_buffer_path(name)) and await is_file(current):
            if state.vc.ignored & {current, *ancestors(current)}:
                return None
            else:
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
