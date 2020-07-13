from asyncio import gather
from typing import AsyncIterator, Iterable, Optional, Sequence, Tuple

from .consts import fm_filetype
from .da import anext
from .fs import is_parent
from .nvim import Buffer, Nvim2, Tabpage, Window
from .types import Settings


async def is_fm_buffer(nvim: Nvim2, buffer: Buffer) -> bool:
    ft = await nvim.api.buf_get_option(buffer, "filetype")
    return ft == fm_filetype


async def find_windows_in_tab(nvim: Nvim2) -> AsyncIterator[Window]:
    async def key_by(window: Window) -> Tuple[int, int]:
        row, col = await nvim.api.win_get_position(window)
        return (col, row)

    tab: Tabpage = await nvim.api.get_current_tabpage()
    windows: Sequence[Window] = await nvim.api.tabpage_list_wins(tab)

    w = [(window, await key_by(window)) for window in windows]

    for window, _ in sorted(w, key=lambda t: t[1]):
        if not await nvim.api.win_get_option(window, "previewwindow"):
            yield window


async def find_fm_windows_in_tab(nvim: Nvim2) -> AsyncIterator[Window]:
    async for window in find_windows_in_tab(nvim):
        buffer: Buffer = await nvim.api.win_get_buf(window)
        if await is_fm_buffer(nvim, buffer=buffer):
            yield window


async def find_non_fm_windows_in_tab(nvim: Nvim2) -> AsyncIterator[Window]:
    async for window in find_windows_in_tab(nvim):
        buffer: Buffer = await nvim.api.win_get_buf(window)
        if not await is_fm_buffer(nvim, buffer=buffer):
            yield window


async def find_window_with_file_in_tab(nvim: Nvim2, file: str) -> AsyncIterator[Window]:
    async for window in find_windows_in_tab(nvim):
        buffer: Buffer = await nvim.api.win_get_buf(window)
        name = await nvim.api.buf_get_name(buffer)
        if name == file:
            yield window


async def find_fm_buffers(nvim: Nvim2) -> AsyncIterator[Buffer]:
    buffers: Sequence[Buffer] = await nvim.api.list_bufs()
    for buffer in buffers:
        if await is_fm_buffer(nvim, buffer=buffer):
            yield buffer


async def find_buffer_with_file(nvim: Nvim2, file: str) -> AsyncIterator[Buffer]:
    buffers: Sequence[Buffer] = await nvim.api.list_bufs()
    for buffer in buffers:
        name = await nvim.api.buf_get_name(buffer)
        if name == file:
            yield buffer


async def new_fm_buffer(nvim: Nvim2) -> Buffer:
    buffer: Buffer = await nvim.api.create_buf(False, True)
    await gather(
        nvim.api.buf_set_option(buffer, "modifiable", False),
        nvim.api.buf_set_option(buffer, "filetype", fm_filetype),
    )
    return buffer


async def new_window(nvim: Nvim2, *, open_left: bool) -> Window:
    split = await nvim.api.get_option("splitright")

    windows: Sequence[Window] = [w async for w in find_windows_in_tab(nvim)]
    focus_win = windows[0] if open_left else windows[-1]
    direction = False if open_left else True

    await nvim.api.set_option("splitright", direction)
    await nvim.api.set_current_win(focus_win)
    await nvim.command("vnew")
    await nvim.api.set_option("splitright", split)

    window: Window = await nvim.api.get_current_win()
    return window


async def resize_fm_windows(nvim: Nvim2, *, settings: Settings) -> None:
    async for window in find_fm_windows_in_tab(nvim):
        await nvim.api.win_set_width(window, settings.width)


async def toggle_shown(nvim: Nvim2, *, settings: Settings) -> None:
    window: Optional[Window] = await anext(find_fm_windows_in_tab(nvim))
    if window:
        await nvim.api.win_close(window, True)
    else:
        buffer: Buffer = await anext(find_fm_buffers(nvim))
        if buffer is None:
            buffer = await new_fm_buffer(nvim)
        window = await new_window(nvim, open_left=settings.open_left)
        await gather(
            nvim.api.win_set_buf(window, buffer),
            nvim.api.win_set_option(window, "number", False),
            nvim.api.win_set_option(window, "signcolumn", "no"),
            nvim.api.win_set_option(window, "cursorline", True),
        )
        await resize_fm_windows(nvim, settings=settings)


async def show_file(nvim: Nvim2, *, settings: Settings, file: str) -> None:
    buffer: Optional[Buffer] = await anext(find_buffer_with_file(nvim, file=file))
    window: Window = await anext(
        find_window_with_file_in_tab(nvim, file=file)
    ) or await anext(find_non_fm_windows_in_tab(nvim)) or await new_window(
        nvim, open_left=not settings.open_left
    )

    await nvim.api.set_current_win(window)
    if buffer is None:
        await nvim.command(f"edit {file}")
    else:
        await nvim.api.win_set_buf(window, buffer)
    await resize_fm_windows(nvim, settings=settings)


async def update_buffers(nvim: Nvim2, lines: Sequence[str]) -> None:

    async for buffer in find_fm_buffers(nvim):
        modifiable = await nvim.api.buf_get_option(buffer, "modifiable")
        await nvim.api.buf_set_option(buffer, "modifiable", True)
        await nvim.api.buf_set_lines(buffer, 0, -1, True, lines)
        await nvim.api.buf_set_option(buffer, "modifiable", modifiable)


async def kill_buffers(nvim: Nvim2, paths: Iterable[str]) -> None:
    buffers: Sequence[Buffer] = await nvim.api.list_bufs()
    for buffer in buffers:
        name = await nvim.api.buf_get_name(buffer)
        if any(is_parent(parent=path, child=name) for path in paths):
            await nvim.command(f"bwipeout! {buffer.number}")
