from asyncio import gather
from itertools import chain
from locale import strxfrm
from os import chdir
from os.path import basename, dirname, exists, join, relpath
from typing import Awaitable, Callable, Dict, Iterator, Optional, Sequence

from pynvim import Nvim

from .cartographer import new as new_root
from .fs import ancestors, copy, cut, is_parent, new, remove, rename, unify_ancestors
from .git import status
from .nvim import (
    Buffer,
    HoldPosition,
    HoldWindowPosition,
    Window,
    buffer_keymap,
    call,
    print,
)
from .state import dump_session, forward
from .state import index as state_index
from .state import is_dir
from .types import Mode, Node, Settings, State
from .wm import (
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
        with HoldPosition(nvim):
            update_buffers(nvim, lines=state.rendered)

    await call(nvim, cont)


def _display_path(path: str, state: State) -> str:
    raw = relpath(path, start=state.root.path)
    return raw.replace("\n", r"\n")


async def _current(nvim: Nvim, state: State, settings: Settings, current: str) -> State:
    if is_parent(parent=state.root.path, child=current):
        paths = {*ancestors(current)} if state.follow else set()
        index = state.index | paths
        new_state = await forward(
            state, settings=settings, index=index, paths=paths, current=current
        )
        return new_state
    else:
        return state


async def a_on_filetype(
    nvim: Nvim, state: State, settings: Settings, bufnr: int
) -> None:
    def cont() -> None:
        buffer = find_buffer(nvim, bufnr)
        if buffer is not None:
            buffer_keymap(nvim, buffer=buffer, keymap=settings.keymap)

    await call(nvim, cont)


async def a_changedir(nvim: Nvim, state: State, settings: Settings) -> State:
    cwd = await call(nvim, nvim.funcs.getcwd)
    chdir(cwd)
    index = state.index | {cwd}
    root = await new_root(cwd, index=index)
    new_state = await forward(state, settings=settings, root=root, index=index)
    return new_state


async def a_follow(nvim: Nvim, state: State, settings: Settings) -> State:
    def cont() -> str:
        buffer = nvim.api.get_current_buf()
        name = nvim.api.buf_get_name(buffer)
        return name

    current = await call(nvim, cont)
    return await _current(nvim, state=state, settings=settings, current=current)


async def a_session(nvim: Nvim, state: State, settings: Settings) -> None:
    dump_session(state)


async def c_quit(nvim: Nvim, state: State, settings: Settings) -> None:
    def cont() -> None:
        kill_fm_windows(nvim, settings=settings)

    await call(nvim, cont)


async def c_open(nvim: Nvim, state: State, settings: Settings) -> State:
    def cont() -> str:
        buffer = nvim.api.get_current_buf()
        name = nvim.api.buf_get_name(buffer)
        toggle_fm_window(nvim, state=state, settings=settings)
        return name

    current = await call(nvim, cont)

    return await _current(nvim, state=state, settings=settings, current=current)


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


async def c_primary(nvim: Nvim, state: State, settings: Settings) -> State:
    node = await _index(nvim, state=state)
    if node:
        if Mode.FOLDER in node.mode:
            paths = {node.path}
            index = state.index ^ paths
            new_state = await forward(
                state, settings=settings, index=index, paths=paths
            )
            return new_state
        else:
            new_state = await forward(state, settings=settings, current=node.path)

            def cont() -> None:
                show_file(nvim, state=new_state, settings=settings)

            await call(nvim, cont)

            return new_state
    else:
        return state


async def c_secondary(nvim: Nvim, state: State, settings: Settings) -> State:
    async with HoldWindowPosition(nvim):
        return await c_primary(nvim, state=state, settings=settings)


async def c_collapse(nvim: Nvim, state: State, settings: Settings) -> State:
    node = await _index(nvim, state=state)
    if node and Mode.FOLDER in node.mode:
        paths = {i for i in state.index if is_parent(parent=node.path, child=i)}
        index = state.index - paths
        new_state = await forward(state, settings=settings, index=index, paths=paths)
        return new_state
    else:
        return state


async def c_refresh(nvim: Nvim, state: State, settings: Settings) -> State:
    paths = {state.root.path}
    vc = await status()
    new_state = await forward(state, settings=settings, vc=vc, paths=paths)
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

    clip = "\n".join(paths)
    clap = ", ".join(paths)
    await gather(nvim.funcs.setreg("+", clip), nvim.funcs.setreg("*", clip))
    await print(nvim, f"📎 {clap}")


async def c_new(nvim: Nvim, state: State, settings: Settings) -> State:
    node = await _index(nvim, state=state)
    if node:
        parent = node.path if is_dir(node) else dirname(node.path)

        def ask() -> Optional[str]:
            resp = nvim.funcs.input("✏️  :")
            return resp

        child = await call(nvim, ask)

        if child:
            name = join(parent, child)
            if exists(name):
                msg = f"⚠️  Exists: {name}"
                await print(nvim, msg, error=True)
                return state
            else:
                try:
                    await new(name)
                except Exception as e:
                    await print(nvim, e, error=True)
                finally:
                    index = state.index | {*ancestors(name)}
                    new_state = await forward(
                        state, settings=settings, index=index, paths={parent}
                    )
                    return new_state
        else:
            return state
    else:
        return state


async def c_rename(nvim: Nvim, state: State, settings: Settings) -> State:
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
            if exists(new_name):
                msg = f"⚠️  Exists: {new_name}"
                await print(nvim, msg, error=True)
                return state
            else:
                try:
                    await rename(prev_name, new_name)
                except Exception as e:
                    await print(nvim, e, error=True)
                finally:
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
            return state
    else:
        return state


async def c_clear(nvim: Nvim, state: State, settings: Settings) -> State:
    new_state = await forward(state, settings=settings, selection=set())
    return new_state


async def c_select(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> State:
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
            return state


async def c_delete(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> State:
    selection = state.selection or {
        node.path for node in await _indices(nvim, state=state, is_visual=is_visual)
    }
    unified = tuple(unify_ancestors(selection))
    if unified:
        display_paths = "\n".join(
            sorted((_display_path(path, state=state) for path in unified), key=strxfrm)
        )

        def ask() -> int:
            resp = nvim.funcs.confirm(f"🗑\n{display_paths}?", "&Yes\n&No\n", 2)
            return resp

        ans = await call(nvim, ask)
        if ans == 1:
            try:
                await remove(unified)
            except Exception as e:
                await print(nvim, e, error=True)
            finally:
                paths = {dirname(path) for path in unified}
                new_selection = set()
                new_state = await forward(
                    state, settings=settings, selection=new_selection, paths=paths
                )

                def cont() -> None:
                    kill_buffers(nvim, paths=selection)

                await call(nvim, cont)
                return new_state
        else:
            return state
    else:
        return state


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
) -> State:
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
            return state
        else:

            msg = "\n".join(
                f"{_display_path(s, state=state)} -> {_display_path(d, state=state)}"
                for s, d in sorted(operations.items(), key=lambda t: strxfrm(t[0]))
            )

            def ask() -> int:
                resp = nvim.funcs.confirm(f"{op_name}\n{msg}?", "&Yes\n&No\n", 2)
                return resp

            ans = await call(nvim, ask)
            if ans == 1:
                try:
                    await action(operations)
                except Exception as e:
                    await print(nvim, e, error=True)
                finally:
                    paths = {
                        dirname(p)
                        for p in chain(operations.keys(), operations.values())
                    }
                    index = state.index | paths
                    new_selection = {
                        dest for dest in operations.values() if exists(dest)
                    }
                    new_state = await forward(
                        state,
                        settings=settings,
                        index=index,
                        selection=new_selection,
                        paths=paths,
                    )

                    def cont() -> None:
                        kill_buffers(nvim, paths=selection)

                    await call(nvim, cont)
                    return new_state
            else:
                return state
    else:
        await print(nvim, "⚠️  -- {name}: nothing selected!", error=True)
        return state


async def c_cut(nvim: Nvim, state: State, settings: Settings) -> State:
    return await _operation(
        nvim, state=state, settings=settings, op_name="Cut", action=cut
    )


async def c_copy(nvim: Nvim, state: State, settings: Settings) -> State:
    return await _operation(
        nvim, state=state, settings=settings, op_name="Copy", action=copy
    )
