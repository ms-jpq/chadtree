from asyncio import gather
from dataclasses import asdict
from os.path import dirname, join
from typing import Optional

from .git import status
from .keymap import keymap
from .nvim import Buffer, Nvim2, Window, find_buffer
from .state import index, is_dir
from .types import Node, Settings, State
from .wm import is_fm_buffer, toggle_shown, update_buffers


async def _index(nvim: Nvim2, state: State) -> Optional[Node]:
    window: Window = await nvim.api.get_current_win()
    row, _ = await nvim.api.win_get_cursor(window)
    row = row - 1
    return index(state, row)


async def _redraw(nvim: Nvim2, state: State) -> None:
    await update_buffers(nvim, lines=state.rendered)


async def a_on_filetype(
    nvim: Nvim2, state: State, settings: Settings, buf: int
) -> None:
    buffer = await find_buffer(nvim, buf)
    await keymap(nvim, buffer=buffer, settings=settings)


async def a_on_bufenter(nvim: Nvim2, state: State, buf: int) -> State:
    buffer = await find_buffer(nvim, buf)
    if await is_fm_buffer(nvim, buffer=buffer):
        git = await status()
        return State(**{**asdict(state), **dict(git=git)})
    else:
        return state


async def a_on_focus(nvim: Nvim2, state: State) -> State:
    git = await status()
    return State(**{**asdict(state), **dict(git=git)})


async def c_open(nvim: Nvim2, state: State, settings: Settings) -> None:
    await toggle_shown(nvim, settings=settings)
    await _redraw(nvim, state=state)


async def c_primary(nvim: Nvim2, state: State) -> State:
    pass


async def c_secondary(nvim: Nvim2, state: State) -> State:
    pass


async def c_refresh(nvim: Nvim2, state: State) -> State:
    pass


async def c_hidden(nvim: Nvim2, state: State) -> State:
    pass


async def c_copy_name(nvim: Nvim2, state: State) -> None:
    node = await _index(nvim, state)
    if node:
        t1 = nvim.funcs.setreg("+", node.path)
        t2 = nvim.funcs.setreg("*", node.path)
        await gather(t1, t2)
        await nvim.print(f"📎 {node}")


async def c_new(nvim: Nvim2, state: State) -> State:
    node = await _index(nvim, state)
    if node:
        parent = node.path if is_dir(node) else dirname(node.path)
        child = await nvim.funcs.input("New name: ")
        new_name = join(parent, child)
        await nvim.print(new_name)
        return state
    else:
        return state


async def c_rename(nvim: Nvim2, state: State) -> State:
    pass


async def c_select(nvim: Nvim2, state: State) -> State:
    pass


async def c_clear(nvim: Nvim2, state: State) -> State:
    pass


async def c_delete(nvim: Nvim2, state: State) -> State:
    pass


async def c_cut(nvim: Nvim2, state: State) -> State:
    pass


async def c_copy(nvim: Nvim2, state: State) -> State:
    pass


async def c_paste(nvim: Nvim2, state: State) -> State:
    pass
