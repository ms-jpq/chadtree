from __future__ import annotations

from asyncio import Future
from typing import Any, Awaitable, Dict, Iterable, Optional, Protocol, Sequence
from uuid import uuid4

from pynvim import Nvim

Tabpage = Any
Window = Any
Buffer = Any


class AsyncedCallable(Protocol):
    def __call__(self, *args: Any) -> Awaitable[Any]:
        pass


class Asynced:
    def __init__(self, nvim: Nvim, attr: str):
        self.__nvim = nvim
        self.__attr = getattr(nvim, attr)

    def __getattr__(self, name: str) -> AsyncedCallable:
        fut: Future = Future()
        fn = getattr(self.__attr, name)

        def f(*args: Any, **kwargs: Any) -> None:
            nonlocal fut
            ret = fn(*args, **kwargs)
            fut.set_result(ret)
            fut = Future()

        def run(*args: Any) -> Awaitable[Any]:
            self.__nvim.async_call(f, *args)
            return fut

        return run


class Nvim2:
    def __init__(self, nvim: Nvim):
        self._nvim = nvim
        self.funcs = Asynced(nvim, "funcs")
        self.api = Asynced(nvim, "api")
        self.command = self.api.command


async def print(
    nvim: Nvim2, message: Any, error: bool = False, flush: bool = True
) -> None:
    write = nvim.api.err_write if error else nvim.api.out_write
    await write(str(message))
    if flush:
        await write("\n")


async def autocmd(
    nvim: Nvim2,
    *,
    events: Iterable[str],
    fn: str,
    filters: Iterable[str] = ("*",),
    modifiers: Iterable[str] = (),
    arg_eval: Iterable[str] = "",
) -> None:
    _events = " ".join(events)
    _filters = " ".join(filters)
    _modifiers = " ".join(modifiers)
    _args = ", ".join(arg_eval)
    name = str(uuid4()).replace("-", "")
    group = f"augroup {name}"
    cls = "  autocmd!"
    cmd = f"  autocmd {_events} {_filters} {_modifiers} call {fn}({_args})"
    group_end = "augroup END"

    instruction = "\n".join((group, cls, cmd, group_end))
    await nvim.command(instruction)


async def buffer_keymap(
    nvim: Nvim2, buffer: Buffer, keymap: Dict[str, Sequence[str]]
) -> None:
    options = {"noremap": True, "silent": True, "nowait": True}

    for function, mappings in keymap.items():
        for mapping in mappings:
            await nvim.api.buf_set_keymap(
                buffer, "n", mapping, f"<cmd>call {function}(0)<cr>", options
            )
            await nvim.api.buf_set_keymap(
                buffer, "v", mapping, f"<esc><cmd>call {function}(1)<cr>", options
            )


async def find_buffer(nvim: Nvim2, bufnr: int) -> Optional[Buffer]:
    buffers: Sequence[Buffer] = await nvim.api.list_bufs()
    for buffer in buffers:
        if buffer.number == bufnr:
            return buffer
    return None


class HoldPosition:
    def __init__(self, nvim: Nvim2):
        self.nvim = nvim

    async def __aenter__(self) -> None:
        self.window = await self.nvim.api.get_current_win()
        self.pos = await self.nvim.api.win_get_cursor(self.window)

    async def __aexit__(self, *_) -> None:
        row, col = self.pos
        buffer: Buffer = await self.nvim.api.win_get_buf(self.window)
        max_rows = await self.nvim.api.buf_line_count(buffer)
        r = min(row, max_rows)
        await self.nvim.api.win_set_cursor(self.window, (r, col))


class HoldWindowPosition:
    def __init__(self, nvim: Nvim2):
        self.nvim = nvim

    async def __aenter__(self) -> None:
        self.window = await self.nvim.api.get_current_win()

    async def __aexit__(self, *_) -> None:
        await self.nvim.api.set_current_win(self.window)
