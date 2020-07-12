from os.path import dirname, join
from typing import Optional

from .cartographer import update
from .da import toggled

# from .git import status
from .keymap import keymap
from .nvim import HoldPosition, HoldWindowPosition, Nvim, Window, find_buffer, print
from .state import forward, index, is_dir
from .types import Mode, Node, Settings, State
from .wm import is_fm_buffer, show_file, toggle_shown, update_buffers


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


def a_on_bufenter(nvim: Nvim, state: State, settings: Settings, buf: int) -> State:
    buffer = find_buffer(nvim, buf)
    if is_fm_buffer(nvim, buffer=buffer):
        return state
    else:
        return state


def a_on_focus(nvim: Nvim, state: State, settings: Settings) -> State:
    return state


def c_open(nvim: Nvim, state: State, settings: Settings) -> None:
    toggle_shown(nvim, settings=settings)
    _redraw(nvim, state=state)


def c_primary(nvim: Nvim, state: State, settings: Settings) -> State:
    node = _index(nvim, state)
    if node:
        with HoldPosition(nvim):
            if Mode.FOLDER in node.mode:
                path = node.path
                index = toggled(state.index, path)
                root = update(state.root, index=index, paths={path})
                new_state = forward(state, settings=settings, root=root, index=index)
                _redraw(nvim, state=new_state)
                return new_state
            else:
                show_file(nvim, settings=settings, file=node.path)
                return state
    else:
        return state


def c_secondary(nvim: Nvim, state: State, settings: Settings) -> State:
    with HoldWindowPosition(nvim):
        return c_primary(nvim, state=state, settings=settings)


def c_refresh(nvim: Nvim, state: State, settings: Settings) -> State:
    path = state.root.path
    root = update(state.root, index=state.index, paths={path})
    new_state = forward(state, settings=settings, root=root)
    _redraw(nvim, state=new_state)
    return state


def c_hidden(nvim: Nvim, state: State, settings: Settings) -> State:
    with HoldPosition(nvim):
        new_state = forward(state, settings=settings, show_hidden=not state.show_hidden)
        _redraw(nvim, state=new_state)
        return new_state


def c_copy_name(nvim: Nvim, state: State, settings: Settings) -> None:
    node = _index(nvim, state)
    if node:
        path = node.path
        nvim.funcs.setreg("+", path)
        nvim.funcs.setreg("*", path)
        print(nvim, f"📎 {path}")


def c_new(nvim: Nvim, state: State, settings: Settings) -> State:
    node = _index(nvim, state)
    if node:
        parent = node.path if is_dir(node) else dirname(node.path)
        child = nvim.funcs.input("New name: ")
        new_name = join(parent, child)
        nvim.print(new_name)
        return state
    else:
        return state


def c_rename(nvim: Nvim, state: State, settings: Settings) -> State:
    return state


def c_select(nvim: Nvim, state: State, settings: Settings) -> State:
    return state


def c_clear(nvim: Nvim, state: State, settings: Settings) -> State:
    pass


def c_delete(nvim: Nvim, state: State, settings: Settings) -> State:
    return state


def c_cut(nvim: Nvim, state: State, settings: Settings) -> State:
    return state


def c_copy(nvim: Nvim, state: State, settings: Settings) -> State:
    return state
