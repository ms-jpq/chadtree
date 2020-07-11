from asyncio import gather
from typing import Iterable, Iterator, Optional, Sequence, Tuple

from .consts import fm_filetype
from .da import anext
from .nvim import Buffer, Nvim2, Tabpage, Window
from .types import Settings


async def is_fm_buffer(nvim: Nvim2, buffer: Buffer) -> bool:
    ft = await nvim.api.buf_get_option(buffer, "filetype")
    return ft == fm_filetype


async def sorted_windows(nvim: Nvim2, windows: Iterable[Window]) -> Sequence[Window]:
    def key_by(window: Window) -> Tuple[int, int]:
        row, col = await nvim.api.win_get_position(window)
        return (col, row)

    keys = await gather(*map(key_by, windows))
    sorted_windows = tuple(w for w, _ in sorted(zip(windows, keys), key=lambda t: t[1]))

    return sorted_windows


async def find_windows_in_tab(nvim: Nvim2) -> Iterator[Window]:
    tab: Tabpage = await nvim.api.get_current_tabpage()
    windows: Sequence[Window] = await nvim.api.tabpage_list_wins(tab)

    for window in await sorted_windows(nvim, windows):
        buffer: Buffer = await nvim.api.win_get_buf(window)
        if await is_fm_buffer(nvim, buffer=buffer):
            yield window


async def find_buffers(nvim: Nvim2) -> Iterator[Buffer]:
    buffers: Sequence[Buffer] = await nvim.api.list_bufs()

    for buffer in buffers:
        if await is_fm_buffer(nvim, buffer=buffer):
            yield buffer


async def new_buf(nvim: Nvim2) -> Buffer:
    buffer: Buffer = await nvim.api.create_buf(False, True)
    t1 = nvim.api.buf_set_option(buffer, "modifiable", False)
    t2 = nvim.api.buf_set_option(buffer, "filetype", fm_filetype)
    await gather(t1, t2)
    return buffer


async def new_window(nvim: Nvim2, buffer: Buffer, settings: Settings) -> Window:
    await nvim.command("vnew")
    window: Window = await nvim.api.get_current_win()
    t1 = nvim.api.win_set_buf(window, buffer)
    t2 = nvim.api.win_set_width(window, settings.width)
    await gather(t1, t2)
    return window


async def toggle_shown(nvim: Nvim2, settings: Settings) -> None:
    window: Optional[Window] = await anext(find_windows_in_tab(nvim), None)
    if window:
        await nvim.api.win_close(window, True)
    else:
        buffer: Buffer = (await anext(find_buffers(nvim), None)) or (
            await new_buf(nvim)
        )
        window = await new_window(nvim, buffer=buffer, settings=settings)


async def update_buffers(nvim: Nvim2, lines: Sequence[str]) -> None:
    async def update(buffer: Buffer) -> None:
        t1 = nvim.api.buf_set_option(buffer, "modifiable", True)
        t2 = nvim.api.buf_set_lines(buffer, 0, -1, True, lines)
        t3 = nvim.api.buf_set_option(buffer, "modifiable", False)
        await gather(t1, t2, t3)

    buffers = await find_buffers(nvim)
    await gather(*map(update, buffers))
