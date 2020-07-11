from asyncio import gather
from dataclasses import asdict
from os.path import dirname, join
from typing import Optional

from pynvim import Nvim

from .git import status
from .keymap import keymap
from .nvim import Buffer, Window
from .state import index, is_dir
from .types import Node, Settings, State
from .wm import is_fm_buffer, toggle_shown, update_buffers


async def print(nvim: Nvim, message: str, error: bool = False) -> None:
    write = nvim.api.err_write if error else nvim.api.out_write
    await write(message + "\n")


async def _index(nvim: Nvim, state: State) -> Optional[Node]:
    window: Window = await nvim.api.get_current_win()
    row, _ = await nvim.api.win_get_cursor(window)
    row = row - 1
    return index(state, row)


async def _redraw(nvim: Nvim, state: State) -> None:
    await update_buffers(nvim, lines=state.rendered)


async def a_on_filetype(nvim: Nvim, state: State, settings: Settings, buf: int) -> None:
    buffer: Buffer = nvim.buffers[buf]
    await keymap(nvim, buffer=buffer, settings=settings)


async def a_on_bufenter(nvim: Nvim, state: State, buf: int) -> State:
    buffer: Buffer = nvim.buffers[buf]
    if await is_fm_buffer(nvim, buffer=buffer):
        git = await status()
        return State(**{**asdict(state), **dict(git=git)})
    else:
        return state


async def a_on_focus(nvim: Nvim, state: State) -> State:
    git = await status()
    return State(**{**asdict(state), **dict(git=git)})


async def c_open(nvim: Nvim, state: State, settings: Settings) -> None:
    await toggle_shown(nvim, settings=settings)


async def c_primary(nvim: Nvim, state: State) -> State:
    pass


async def c_secondary(nvim: Nvim, state: State) -> State:
    pass


async def c_refresh(nvim: Nvim, state: State) -> State:
    pass


async def c_hidden(nvim: Nvim, state: State) -> State:
    pass


async def c_copy_name(nvim: Nvim, state: State) -> None:
    node = await _index(nvim, state)
    if node:
        t1 = nvim.funcs.setreg("+", node.path)
        t2 = nvim.funcs.setreg("*", node.path)
        await gather(t1, t2)
        await print(nvim, f"📎 {node}")


async def c_new(nvim: Nvim, state: State) -> State:
    node = await _index(nvim, state)
    if node:
        parent = node.path if is_dir(node) else dirname(node.path)
        child = await nvim.funcs.input("New name: ")
        new_name = join(parent, child)
        await print(nvim, new_name)
        return state
    else:
        return state


async def c_rename(nvim: Nvim, state: State) -> State:
    pass


async def c_select(nvim: Nvim, state: State) -> State:
    pass


async def c_clear(nvim: Nvim, state: State) -> State:
    pass


async def c_delete(nvim: Nvim, state: State) -> State:
    pass


async def c_cut(nvim: Nvim, state: State) -> State:
    pass


async def c_copy(nvim: Nvim, state: State) -> State:
    pass


async def c_paste(nvim: Nvim, state: State) -> State:
    pass
