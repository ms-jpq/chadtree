from os.path import basename, dirname, exists, join, relpath
from typing import AsyncIterator, Awaitable, Callable, Dict, Optional, Sequence

from .fs import ancestors, copy, cut, is_parent, new, remove, rename, unify
from .git import status
from .keymap import keymap
from .nvim import (
    Buffer,
    HoldPosition,
    HoldWindowPosition,
    Nvim2,
    Window,
    find_buffer,
    print,
)
from .state import forward, index, is_dir
from .types import Mode, Node, Settings, State
from .wm import kill_buffers, kill_fm_windows, show_file, toggle_shown, update_buffers


async def _index(nvim: Nvim2, state: State) -> Optional[Node]:
    window: Window = await nvim.api.get_current_win()
    row, _ = await nvim.api.win_get_cursor(window)
    row = row - 1
    return index(state, row)


async def _indices(nvim: Nvim2, state: State, is_visual: bool) -> AsyncIterator[Node]:
    if is_visual:
        buffer: Buffer = await nvim.api.get_current_buf()
        r1, _ = await nvim.api.buf_get_mark(buffer, "<")
        r2, _ = await nvim.api.buf_get_mark(buffer, ">")
        for row in range(r1 - 1, r2):
            node = index(state, row)
            if node:
                yield node
    else:
        window: Window = await nvim.api.get_current_win()
        row, _ = await nvim.api.win_get_cursor(window)
        row = row - 1
        node = index(state, row)
        if node:
            yield node


async def redraw(nvim: Nvim2, state: State) -> None:
    async with HoldPosition(nvim):
        await update_buffers(nvim, lines=state.rendered)


def _display_path(path: str, state: State) -> str:
    raw = relpath(path, start=state.root.path)
    return raw.replace("\n", r"\n")


async def a_on_filetype(
    nvim: Nvim2, state: State, settings: Settings, buf: int
) -> None:
    buffer = await find_buffer(nvim, buf)
    if buffer is not None:
        await keymap(nvim, buffer=buffer, settings=settings)


async def c_quit(nvim: Nvim2, state: State, settings: Settings) -> None:
    await kill_fm_windows(nvim, settings=settings)


async def c_open(nvim: Nvim2, state: State, settings: Settings) -> None:
    await toggle_shown(nvim, settings=settings)
    await redraw(nvim, state=state)


async def c_primary(nvim: Nvim2, state: State, settings: Settings) -> State:
    node = await _index(nvim, state=state)
    if node:
        if Mode.FOLDER in node.mode:
            paths = {node.path}
            index = state.index ^ paths
            new_state = await forward(
                state, settings=settings, index=index, paths=paths
            )
            await redraw(nvim, state=new_state)
            return new_state
        else:
            await show_file(nvim, settings=settings, file=node.path)
            return state
    else:
        return state


async def c_secondary(nvim: Nvim2, state: State, settings: Settings) -> State:
    async with HoldWindowPosition(nvim):
        return await c_primary(nvim, state=state, settings=settings)


async def c_collapse(nvim: Nvim2, state: State, settings: Settings) -> State:
    node = await _index(nvim, state=state)
    if node and Mode.FOLDER in node.mode:
        paths = {i for i in state.index if is_parent(parent=node.path, child=i)}
        index = state.index - paths
        new_state = await forward(state, settings=settings, index=index, paths=paths)
        await redraw(nvim, state=new_state)
        return new_state
    else:
        return state


async def c_refresh(nvim: Nvim2, state: State, settings: Settings) -> State:
    paths = {state.root.path}
    vc = await status()
    new_state = await forward(state, settings=settings, vc=vc, paths=paths)
    await redraw(nvim, state=new_state)
    return new_state


async def c_hidden(nvim: Nvim2, state: State, settings: Settings) -> State:
    new_state = await forward(
        state, settings=settings, show_hidden=not state.show_hidden
    )
    await redraw(nvim, state=new_state)
    return new_state


async def c_follow(nvim: Nvim2, state: State, settings: Settings) -> State:
    new_state = await forward(state, settings=settings, follow=not state.follow)
    return new_state


async def c_copy_name(
    nvim: Nvim2, state: State, settings: Settings, is_visual: bool
) -> None:
    paths: Sequence[str] = [
        n.path async for n in _indices(nvim, state=state, is_visual=is_visual)
    ]
    clip = "\n".join(paths)
    clap = ", ".join(paths)
    await nvim.funcs.setreg("+", clip)
    await nvim.funcs.setreg("*", clip)
    await print(nvim, f"📎 {clap}")


async def c_new(nvim: Nvim2, state: State, settings: Settings) -> State:
    node = await _index(nvim, state=state)
    if node:
        parent = node.path if is_dir(node) else dirname(node.path)
        child = await nvim.funcs.input("✏️  :")
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
                await redraw(nvim, state=new_state)
                return new_state
    else:
        return state


async def c_rename(nvim: Nvim2, state: State, settings: Settings) -> State:
    node = await _index(nvim, state=state)
    if node:
        prev_name = node.path
        parent = state.root.path
        rel_path = relpath(prev_name, start=parent)
        child = await nvim.funcs.input("✏️  :", rel_path)
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
                await redraw(nvim, state=new_state)
                await kill_buffers(nvim, paths=(prev_name,))
                return new_state
    else:
        return state


async def c_clear(nvim: Nvim2, state: State, settings: Settings) -> State:
    new_state = await forward(state, settings=settings, selection=set())
    await redraw(nvim, state=new_state)
    return new_state


async def c_select(
    nvim: Nvim2, state: State, settings: Settings, is_visual: bool
) -> State:
    nodes = iter([n async for n in _indices(nvim, state=state, is_visual=is_visual)])
    if is_visual:
        selection = state.selection ^ {n.path for n in nodes}
        new_state = await forward(state, settings=settings, selection=selection)
        await redraw(nvim, state=new_state)
        return new_state
    else:
        node = next(nodes, None)
        if node:
            selection = state.selection ^ {node.path}
            new_state = await forward(state, settings=settings, selection=selection)
            await redraw(nvim, state=new_state)
            return new_state
        else:
            return state


async def c_delete(nvim: Nvim2, state: State, settings: Settings) -> State:
    node = await _index(nvim, state=state)
    selection = state.selection or ({node.path} if node else set())
    if selection:
        unified = tuple(unify(selection))
        display_paths = "\n".join(_display_path(path, state=state) for path in unified)
        ans = await nvim.funcs.confirm(f"🗑  {display_paths}?", "&Yes\n&No\n", 2)
        if ans == 1:
            try:
                await remove(unified)
                await print(nvim, unified)
            except Exception as e:
                await print(nvim, e, error=True)
            finally:
                paths = {dirname(path) for path in unified}
                new_state = await forward(state, settings=settings, paths=paths)
                await redraw(nvim, state=new_state)
                await kill_buffers(nvim, paths=selection)
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
    nvim: Nvim2,
    *,
    state: State,
    settings: Settings,
    name: str,
    action: Callable[[Dict[str, str]], Awaitable[None]],
) -> State:
    node = await _index(nvim, state=state)
    selection = state.selection
    if selection and node:
        operations = {src: _find_dest(src, node) for src in selection}
        pre_existing = {s: d for s, d in operations.items() if exists(d)}
        if pre_existing:
            msg = ", ".join(
                f"{_display_path(s, state=state)} -> {_display_path(d, state=state)}"
                for s, d in pre_existing.items()
            )
            await print(
                nvim, f"⚠️  -- {name}: path(s) already exist! :: {msg}", error=True
            )
            return state
        else:
            try:
                await action(operations)
            except Exception as e:
                await print(nvim, e, error=True)
            finally:
                paths = {
                    *operations.values(),
                    *(dirname(src) for src in operations.keys()),
                }
                index = state.index | paths
                new_state = await forward(
                    state, settings=settings, index=index, paths=paths
                )
                await redraw(nvim, state=new_state)
                await kill_buffers(nvim, paths=selection)
                return new_state
    else:
        await print(nvim, "⚠️  -- {name}: nothing selected!", error=True)
        return state


async def c_cut(nvim: Nvim2, state: State, settings: Settings) -> State:
    return await _operation(
        nvim, state=state, settings=settings, name="Cut", action=cut
    )


async def c_copy(nvim: Nvim2, state: State, settings: Settings) -> State:
    return await _operation(
        nvim, state=state, settings=settings, name="Copy", action=copy
    )
