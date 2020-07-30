from asyncio import gather, get_running_loop
from itertools import chain
from locale import strxfrm
from os import linesep
from os.path import basename, dirname, exists, isdir, join, relpath, sep
from typing import Awaitable, Callable, Dict, Iterator, Optional, Sequence, Set, Tuple

from pynvim import Nvim
from pynvim.api.buffer import Buffer
from pynvim.api.window import Window

from .cartographer import new as new_root
from .fs import (
    ancestors,
    copy,
    cut,
    fs_exists,
    is_parent,
    new,
    remove,
    rename,
    unify_ancestors,
)
from .git import status
from .nvim import HoldPosition, HoldWindowPosition, call, getcwd, print
from .opener import OpenError, open_gui
from .quickfix import quickfix
from .state import dump_session, forward
from .state import index as state_index
from .state import is_dir
from .types import Index, Mode, Node, Selection, Settings, State
from .wm import (
    find_current_buffer_name,
    is_fm_buffer,
    kill_buffers,
    kill_fm_windows,
    resize_fm_windows,
    show_file,
    toggle_fm_window,
    update_buffers,
)


def find_buffer(nvim: Nvim, bufnr: int) -> Optional[Buffer]:
    buffers: Sequence[Buffer] = nvim.api.list_bufs()
    for buffer in buffers:
        if buffer.number == bufnr:
            return buffer
    return None


async def _index(nvim: Nvim, state: State) -> Optional[Node]:
    def cont() -> Optional[Node]:
        window: Window = nvim.api.get_current_win()
        buffer: Buffer = nvim.api.win_get_buf(window)
        if is_fm_buffer(nvim, buffer=buffer):
            row, _ = nvim.api.win_get_cursor(window)
            row = row - 1
            return state_index(state, row)
        else:
            return None

    return await call(nvim, cont)


async def _indices(nvim: Nvim, state: State, is_visual: bool) -> Sequence[Node]:
    def step() -> Iterator[Node]:
        if is_visual:
            buffer: Buffer = nvim.api.get_current_buf()
            r1, _ = nvim.api.buf_get_mark(buffer, "<")
            r2, _ = nvim.api.buf_get_mark(buffer, ">")
            for row in range(r1 - 1, r2):
                node = state_index(state, row)
                if node:
                    yield node
        else:
            window: Window = nvim.api.get_current_win()
            row, _ = nvim.api.win_get_cursor(window)
            row = row - 1
            node = state_index(state, row)
            if node:
                yield node

    def cont() -> Sequence[Node]:
        return tuple(step())

    return await call(nvim, cont)


async def redraw(nvim: Nvim, state: State) -> None:
    def cont() -> None:
        window: Window = nvim.api.get_current_win()
        buffer: Buffer = nvim.api.win_get_buf(window)
        if is_fm_buffer(nvim, buffer=buffer):
            with HoldPosition(nvim):
                update_buffers(nvim, rendering=state.rendered)
        else:
            update_buffers(nvim, rendering=state.rendered)

    await call(nvim, cont)


def _display_path(path: str, state: State) -> str:
    raw = relpath(path, start=state.root.path)
    name = raw.replace(linesep, r"\n")
    if isdir(path):
        name = f"{name}{sep}"
    return name


async def _current(
    nvim: Nvim, state: State, settings: Settings, current: str
) -> Optional[State]:
    if is_parent(parent=state.root.path, child=current):
        paths: Set[str] = {*ancestors(current)} if state.follow else set()
        index = state.index | paths
        new_state = await forward(
            state, settings=settings, index=index, paths=paths, current=current
        )
        return new_state
    else:
        return None


async def a_changedir(nvim: Nvim, state: State, settings: Settings) -> State:
    cwd = await getcwd(nvim)
    index = state.index | {cwd}
    root = await new_root(cwd, index=index)
    new_state = await forward(state, settings=settings, root=root, index=index)
    return new_state


async def a_follow(nvim: Nvim, state: State, settings: Settings) -> Optional[State]:
    def cont() -> str:
        name = find_current_buffer_name(nvim)
        return name

    current = await call(nvim, cont)
    if current:
        return await _current(nvim, state=state, settings=settings, current=current)
    else:
        return None


async def a_session(nvim: Nvim, state: State, settings: Settings) -> None:
    dump_session(state)


async def a_quickfix(nvim: Nvim, state: State, settings: Settings) -> State:
    qf = await quickfix(nvim)
    new_state = await forward(state, settings=settings, qf=qf)
    return new_state


async def c_quit(nvim: Nvim, state: State, settings: Settings) -> None:
    def cont() -> None:
        kill_fm_windows(nvim, settings=settings)

    await call(nvim, cont)


async def c_open(nvim: Nvim, state: State, settings: Settings) -> State:
    def cont() -> str:
        name = find_current_buffer_name(nvim)
        toggle_fm_window(nvim, state=state, settings=settings)
        return name

    current = await call(nvim, cont)

    new_state = await _current(nvim, state=state, settings=settings, current=current)
    if new_state:
        return new_state
    else:
        return state


async def c_resize(
    nvim: Nvim, state: State, settings: Settings, direction: Callable[[int, int], int]
) -> State:
    new_state = await forward(
        state, settings=settings, width=direction(state.width, 10)
    )

    def cont() -> None:
        resize_fm_windows(nvim, width=new_state.width)

    await call(nvim, cont)
    return new_state


async def _click(
    nvim: Nvim, state: State, settings: Settings, hold_window: bool
) -> Optional[State]:
    node = await _index(nvim, state=state)
    if node:
        if Mode.orphan_link in node.mode:
            name = node.name
            await print(nvim, f"⚠️  cannot open dead link: {name}", error=True)
            return None
        else:
            if Mode.folder in node.mode:
                paths = {node.path}
                index = state.index ^ paths
                new_state = await forward(
                    state, settings=settings, index=index, paths=paths
                )
                return new_state
            else:
                new_state = await forward(state, settings=settings, current=node.path)

                def cont() -> None:
                    if hold_window:
                        with HoldWindowPosition(nvim):
                            show_file(nvim, state=new_state, settings=settings)
                    else:
                        show_file(nvim, state=new_state, settings=settings)

                await call(nvim, cont)

                return new_state
    else:
        return None


async def c_primary(nvim: Nvim, state: State, settings: Settings) -> Optional[State]:
    return await _click(nvim, state=state, settings=settings, hold_window=False)


async def c_secondary(nvim: Nvim, state: State, settings: Settings) -> Optional[State]:
    return await _click(nvim, state=state, settings=settings, hold_window=True)


async def c_collapse(nvim: Nvim, state: State, settings: Settings) -> Optional[State]:
    node = await _index(nvim, state=state)
    if node and Mode.folder in node.mode:
        paths = {
            i
            for i in state.index
            if i == node.path or is_parent(parent=node.path, child=i)
        }
        index = state.index - paths
        new_state = await forward(state, settings=settings, index=index, paths=paths)
        return new_state
    else:
        return None


async def c_refresh(nvim: Nvim, state: State, settings: Settings) -> State:
    def co() -> str:
        current = find_current_buffer_name(nvim)
        return current

    loop = get_running_loop()
    cwd, current = await gather(getcwd(nvim), call(nvim, co))
    paths = {cwd}
    new_current = current if is_parent(parent=cwd, child=current) else None

    def cont() -> Tuple[Index, Selection]:
        index = {i for i in state.index if exists(i)} | paths
        selection = {s for s in state.selection if exists(s)}
        return index, selection

    index, selection = await loop.run_in_executor(None, cont)
    current_paths: Set[str] = {*ancestors(current)} if state.follow else set()
    new_index = index if new_current is None else index | current_paths

    qf, vc = await gather(quickfix(nvim), status())
    new_state = await forward(
        state,
        settings=settings,
        index=new_index,
        selection=selection,
        qf=qf,
        vc=vc,
        paths=paths,
        current=new_current,
    )
    return new_state


async def c_hidden(nvim: Nvim, state: State, settings: Settings) -> State:
    new_state = await forward(
        state, settings=settings, show_hidden=not state.show_hidden
    )
    return new_state


async def c_follow(nvim: Nvim, state: State, settings: Settings) -> State:
    new_state = await forward(state, settings=settings, follow=not state.follow)
    await print(nvim, f"🐶 follow mode: {new_state.follow}")
    return new_state


async def c_copy_name(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> None:
    nodes = await _indices(nvim, state=state, is_visual=is_visual)
    paths = tuple(n.path for n in nodes)

    clip = linesep.join(paths)
    clap = ", ".join(paths)

    def cont() -> None:
        nvim.funcs.setreg("+", clip)
        nvim.funcs.setreg("*", clip)

    await call(nvim, cont)
    await print(nvim, f"📎 {clap}")


async def c_new(nvim: Nvim, state: State, settings: Settings) -> Optional[State]:
    node = await _index(nvim, state=state) or state.root
    parent = node.path if is_dir(node) else dirname(node.path)

    def ask() -> Optional[str]:
        resp = nvim.funcs.input("✏️  :")
        return resp

    child = await call(nvim, ask)

    if child:
        name = join(parent, child)
        if await fs_exists(name):
            msg = f"⚠️  Exists: {name}"
            await print(nvim, msg, error=True)
            return state
        else:
            try:
                await new(name)
            except Exception as e:
                await print(nvim, e, error=True)
                return await c_refresh(nvim, state=state, settings=settings)
            else:
                paths = {*ancestors(name)}
                index = state.index | paths
                new_state = await forward(
                    state, settings=settings, index=index, paths=paths
                )
                return new_state
    else:
        return None


async def c_rename(nvim: Nvim, state: State, settings: Settings) -> Optional[State]:
    node = await _index(nvim, state=state)
    if node:
        prev_name = node.path
        parent = state.root.path
        rel_path = relpath(prev_name, start=parent)

        def ask() -> Optional[str]:
            resp = nvim.funcs.input("✏️  :", rel_path)
            return resp

        child = await call(nvim, ask)
        if child:
            new_name = join(parent, child)
            new_parent = dirname(new_name)
            if await fs_exists(new_name):
                msg = f"⚠️  Exists: {new_name}"
                await print(nvim, msg, error=True)
                return state
            else:
                try:
                    await rename(prev_name, new_name)
                except Exception as e:
                    await print(nvim, e, error=True)
                    return await c_refresh(nvim, state=state, settings=settings)
                else:
                    paths = {parent, new_parent, *ancestors(new_parent)}
                    index = state.index | paths
                    new_state = await forward(
                        state, settings=settings, index=index, paths=paths
                    )

                    def cont() -> None:
                        kill_buffers(nvim, paths=(prev_name,))

                    await call(nvim, cont)
                    return new_state
        else:
            return None
    else:
        return None


async def c_clear(nvim: Nvim, state: State, settings: Settings) -> State:
    new_state = await forward(state, settings=settings, selection=set())
    return new_state


async def c_select(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Optional[State]:
    nodes = iter(await _indices(nvim, state=state, is_visual=is_visual))
    if is_visual:
        selection = state.selection ^ {n.path for n in nodes}
        new_state = await forward(state, settings=settings, selection=selection)
        return new_state
    else:
        node = next(nodes, None)
        if node:
            selection = state.selection ^ {node.path}
            new_state = await forward(state, settings=settings, selection=selection)
            return new_state
        else:
            return None


async def c_delete(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Optional[State]:
    selection = state.selection or {
        node.path for node in await _indices(nvim, state=state, is_visual=is_visual)
    }
    unified = tuple(unify_ancestors(selection))
    if unified:
        display_paths = linesep.join(
            sorted((_display_path(path, state=state) for path in unified), key=strxfrm)
        )

        def ask() -> int:
            resp = nvim.funcs.confirm(
                f"🗑{linesep}{display_paths}?", f"&Yes{linesep}&No{linesep}", 2
            )
            return resp

        ans = await call(nvim, ask)
        if ans == 1:
            try:
                await remove(unified)
            except Exception as e:
                await print(nvim, e, error=True)
                return await c_refresh(nvim, state=state, settings=settings)
            else:
                paths = {dirname(path) for path in unified}
                new_state = await forward(
                    state, settings=settings, selection=set(), paths=paths
                )

                def cont() -> None:
                    kill_buffers(nvim, paths=selection)

                await call(nvim, cont)
                return new_state
        else:
            return None
    else:
        return None


def _find_dest(src: str, node: Node) -> str:
    name = basename(src)
    parent = node.path if is_dir(node) else dirname(node.path)
    dst = join(parent, name)
    return dst


async def _operation(
    nvim: Nvim,
    *,
    state: State,
    settings: Settings,
    op_name: str,
    action: Callable[[Dict[str, str]], Awaitable[None]],
) -> Optional[State]:
    node = await _index(nvim, state=state)
    selection = state.selection
    unified = tuple(unify_ancestors(selection))
    if unified and node:
        operations = {src: _find_dest(src, node) for src in unified}
        pre_existing = {s: d for s, d in operations.items() if exists(d)}
        if pre_existing:
            msg = ", ".join(
                f"{_display_path(s, state=state)} -> {_display_path(d, state=state)}"
                for s, d in sorted(pre_existing.items(), key=lambda t: strxfrm(t[0]))
            )
            await print(
                nvim, f"⚠️  -- {op_name}: path(s) already exist! :: {msg}", error=True
            )
            return None
        else:

            msg = linesep.join(
                f"{_display_path(s, state=state)} -> {_display_path(d, state=state)}"
                for s, d in sorted(operations.items(), key=lambda t: strxfrm(t[0]))
            )

            def ask() -> int:
                resp = nvim.funcs.confirm(
                    f"{op_name}{linesep}{msg}?", f"&Yes{linesep}&No{linesep}", 2
                )
                return resp

            ans = await call(nvim, ask)
            if ans == 1:
                try:
                    await action(operations)
                except Exception as e:
                    await print(nvim, e, error=True)
                    return await c_refresh(nvim, state=state, settings=settings)
                else:
                    paths = {
                        dirname(p)
                        for p in chain(operations.keys(), operations.values())
                    }
                    index = state.index | paths
                    new_state = await forward(
                        state,
                        settings=settings,
                        index=index,
                        selection=set(),
                        paths=paths,
                    )

                    def cont() -> None:
                        kill_buffers(nvim, paths=selection)

                    await call(nvim, cont)
                    return new_state
            else:
                return None
    else:
        await print(nvim, "⚠️  -- {name}: nothing selected!", error=True)
        return None


async def c_cut(nvim: Nvim, state: State, settings: Settings) -> Optional[State]:
    return await _operation(
        nvim, state=state, settings=settings, op_name="Cut", action=cut
    )


async def c_copy(nvim: Nvim, state: State, settings: Settings) -> Optional[State]:
    return await _operation(
        nvim, state=state, settings=settings, op_name="Copy", action=copy
    )


async def c_open_system(nvim: Nvim, state: State, settings: Settings) -> None:
    node = await _index(nvim, state=state)
    if node:
        try:
            await open_gui(node.path)
        except OpenError as e:
            await print(nvim, e)
