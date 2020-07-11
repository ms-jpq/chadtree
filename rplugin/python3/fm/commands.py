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


def print(nvim: Nvim, message: str, error: bool = False) -> None:
    write = nvim.err_write if error else nvim.out_write
    write(message)
    write("\n")


def _index(nvim: Nvim, state: State) -> Optional[Node]:
    window: Window = nvim.current.window
    row, _ = nvim.api.win_get_cursor(window)
    row = row - 1
    return index(state, row)


def _redraw(nvim: Nvim, state: State) -> None:
    update_buffers(nvim, lines=state.rendered)


async def a_on_filetype(nvim: Nvim, state: State, settings: Settings, buf: int) -> None:
    buffer: Buffer = nvim.buffers[buf]
    keymap(nvim, buffer=buffer, settings=settings)


async def a_on_bufenter(nvim: Nvim, state: State, buf: int) -> State:
    buffer: Buffer = nvim.buffers[buf]
    if is_fm_buffer(nvim, buffer=buffer):
        git = await status()
        return State(**{**asdict(state), **dict(git=git)})
    else:
        return state


async def a_on_focus(nvim: Nvim, state: State) -> State:
    git = await status()
    return State(**{**asdict(state), **dict(git=git)})


async def c_open(nvim: Nvim, state: State, settings: Settings) -> None:
    toggle_shown(nvim, settings=settings)


async def c_primary(nvim: Nvim, state: State) -> State:
    pass


async def c_secondary(nvim: Nvim, state: State) -> State:
    pass


async def c_refresh(nvim: Nvim, state: State) -> State:
    pass


async def c_hidden(nvim: Nvim, state: State) -> State:
    pass


async def c_copy_name(nvim: Nvim, state: State) -> None:
    node = _index(nvim, state)
    if node:
        nvim.funcs.setreg("+", node.path)
        nvim.funcs.setreg("*", node.path)
        print(nvim, f"📎 {node}")


async def c_new(nvim: Nvim, state: State) -> State:
    node = _index(nvim, state)
    if node:
        parent = node.path if is_dir(node) else dirname(node.path)
        child = nvim.funcs.input("New name: ")
        new_name = join(parent, child)
        print(nvim, new_name)
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
