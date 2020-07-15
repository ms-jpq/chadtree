from asyncio import Future
from typing import Any, Awaitable, Callable, Dict, Iterable, Optional, Sequence, TypeVar
from uuid import uuid4

from pynvim import Nvim

Tabpage = Any
Window = Any
Buffer = Any

T = TypeVar("T")


def call(nvim: Nvim, fn: Callable[[], T]) -> Awaitable[T]:
    fut: Future = Future()

    def cont() -> None:
        try:
            ret = fn()
        except Exception as e:
            fut.set_exception(e)
        else:
            fut.set_result(ret)

    nvim.async_call(cont)
    return fut


async def print(
    nvim: Nvim, message: Any, error: bool = False, flush: bool = True
) -> None:
    write = nvim.api.err_write if error else nvim.api.out_write

    def cont() -> None:
        write(str(message))
        if flush:
            write("\n")

    await call(nvim, cont)


async def autocmd(
    nvim: Nvim,
    *,
    events: Iterable[str],
    fn: str,
    filters: Iterable[str] = ("*",),
    modifiers: Iterable[str] = (),
    arg_eval: Iterable[str] = (),
) -> None:
    _events = ",".join(events)
    _filters = " ".join(filters)
    _modifiers = " ".join(modifiers)
    _args = ", ".join(arg_eval)
    group = f"augroup {uuid4()}"
    cls = "autocmd!"
    cmd = f"autocmd {_events} {_filters} {_modifiers} call {fn}({_args})"
    group_end = "augroup END"

    def cont() -> None:
        nvim.api.command(group)
        nvim.api.command(cls)
        nvim.api.command(cmd)
        nvim.api.command(group_end)

    await call(nvim, cont)


async def buffer_keymap(
    nvim: Nvim, buffer: Buffer, keymap: Dict[str, Sequence[str]]
) -> None:
    options = {"noremap": True, "silent": True, "nowait": True}

    def cont() -> None:
        for function, mappings in keymap.items():
            for mapping in mappings:
                nvim.api.buf_set_keymap(
                    buffer, "n", mapping, f"<cmd>call {function}(v:false)<cr>", options
                )
                nvim.api.buf_set_keymap(
                    buffer,
                    "v",
                    mapping,
                    f"<esc><cmd>call {function}(v:true)<cr>",
                    options,
                )

    await call(nvim, cont)


class HoldPosition:
    def __init__(self, nvim: Nvim):
        self.nvim = nvim

    def __enter__(self) -> None:
        self.window = self.nvim.api.get_current_win()
        self.pos = self.nvim.api.win_get_cursor(self.window)

    def __exit__(self, *_) -> None:
        row, col = self.pos
        buffer: Buffer = self.nvim.api.win_get_buf(self.window)
        max_rows = self.nvim.api.buf_line_count(buffer)
        r = min(row, max_rows)
        self.nvim.api.win_set_cursor(self.window, (r, col))


class HoldWindowPosition:
    def __init__(self, nvim: Nvim):
        self.nvim = nvim

    async def __aenter__(self) -> None:
        self.window = await call(self.nvim, self.nvim.api.get_current_win)

    async def __aexit__(self, *_) -> None:
        def cont() -> None:
            try:
                self.nvim.api.set_current_win(self.window)
            except Exception:
                pass

        await call(self.nvim, cont)
