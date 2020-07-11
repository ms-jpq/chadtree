from dataclasses import asdict
from os.path import dirname, join
from typing import Optional

from .cartographer import update

# from .git import status
from .keymap import keymap
from .nvim import Nvim, Window, find_buffer, print
from .state import index, is_dir
from .types import Mode, Node, Settings, State
from .wm import find_windows_in_tab, is_fm_buffer, toggle_shown, update_buffers


def _index(nvim: Nvim, state: State) -> Optional[Node]:
    window: Window = nvim.api.get_current_win()
    row, _ = nvim.api.win_get_cursor(window)
    row = row - 1
    return index(state, row)


def _redraw(nvim: Nvim, state: State) -> None:
    update_buffers(nvim, lines=state.rendered)


def a_on_filetype(nvim: Nvim, state: State, settings: Settings, buf: int) -> None:
    buffer = find_buffer(nvim, buf)
    if buffer:
        keymap(nvim, buffer=buffer, settings=settings)


def a_on_bufenter(nvim: Nvim, state: State, buf: int) -> State:
    buffer = find_buffer(nvim, buf)
    if is_fm_buffer(nvim, buffer=buffer):
        return state
    else:
        return state


def a_on_focus(nvim: Nvim, state: State) -> State:
    window = next(find_windows_in_tab(nvim), None)
    if window:
        return state
    else:
        return state


def c_open(nvim: Nvim, state: State, settings: Settings) -> None:
    toggle_shown(nvim, settings=settings)
    _redraw(nvim, state=state)


def c_primary(nvim: Nvim, state: State) -> State:
    node = _index(nvim, state)
    if node:
        print(nvim, node)
        if Mode.FOLDER in node.mode:
            paths = {node.path}
            root = update(state.root, index=state.index, paths=paths)
            index = state.index | paths
            new_state = State(**{**asdict(state), **dict(root=root, index=index)})
            _redraw(nvim, state=new_state)
            return new_state
        else:
            return state
    else:
        return state


def c_secondary(nvim: Nvim, state: State) -> State:
    return state


def c_refresh(nvim: Nvim, state: State) -> State:
    return state


def c_hidden(nvim: Nvim, state: State) -> State:
    return state


def c_copy_name(nvim: Nvim, state: State) -> None:
    node = _index(nvim, state)
    if node:
        nvim.funcs.setreg("+", node.path)
        nvim.funcs.setreg("*", node.path)
        nvim.print(f"📎 {node}")


def c_new(nvim: Nvim, state: State) -> State:
    node = _index(nvim, state)
    if node:
        parent = node.path if is_dir(node) else dirname(node.path)
        child = nvim.funcs.input("New name: ")
        new_name = join(parent, child)
        nvim.print(new_name)
        return state
    else:
        return state


def c_rename(nvim: Nvim, state: State) -> State:
    return state


def c_select(nvim: Nvim, state: State) -> State:
    return state


def c_clear(nvim: Nvim, state: State) -> State:
    pass


def c_delete(nvim: Nvim, state: State) -> State:
    return state


def c_cut(nvim: Nvim, state: State) -> State:
    return state


def c_copy(nvim: Nvim, state: State) -> State:
    return state


def c_paste(nvim: Nvim, state: State) -> State:
    return state
