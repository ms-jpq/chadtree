from typing import Iterable, Iterator, Optional, Sequence, Tuple

from pynvim import Nvim

from .consts import fm_filetype
from .nvim import Buffer, Tabpage, Window
from .types import Settings


def is_fm_buffer(nvim: Nvim, buffer: Buffer) -> bool:
    ft = nvim.api.buf_get_option(buffer, "filetype")
    return ft == fm_filetype


def sorted_windows(nvim: Nvim, window: Iterable[Window]) -> Sequence[Window]:
    def key_by(window: Window) -> Tuple[int, int]:
        row, col = nvim.api.win_get_position(window)
        return (col, row)

    return sorted(window, key=key_by)


def find_windows_in_tab(nvim: Nvim) -> Iterator[Window]:
    tab: Tabpage = nvim.current.tabpage
    windows: Sequence[Window] = nvim.api.tabpage_list_wins(tab)

    for window in sorted_windows(nvim, windows):
        buffer: Buffer = nvim.api.win_get_buf(window)
        if is_fm_buffer(nvim, buffer=buffer):
            yield window


def find_buffers(nvim: Nvim) -> Iterator[Buffer]:
    buffers: Sequence[Buffer] = nvim.buffers

    for buffer in buffers:
        if is_fm_buffer(nvim, buffer=buffer):
            yield buffer


def new_buf(nvim: Nvim) -> Buffer:
    buffer: Buffer = nvim.api.create_buf(False, True)
    nvim.api.buf_set_option(buffer, "filetype", fm_filetype)
    return buffer


def new_window(nvim: Nvim, buffer: Buffer, settings: Settings) -> Window:
    nvim.command("vnew")
    window: Window = nvim.windows[0]
    nvim.api.win_set_buf(window, buffer)
    nvim.api.win_set_width(window, settings.width)
    return window


def toggle_shown(nvim: Nvim, settings: Settings) -> None:
    window: Optional[Window] = next(find_windows_in_tab(nvim), None)
    if window:
        nvim.api.win_close(window, True)
    else:
        buffer: Buffer = next(find_buffers(nvim), None) or new_buf(nvim)
        window = new_window(nvim, buffer=buffer, settings=settings)


def update_buffers(nvim: Nvim, lines: Sequence[str]) -> None:
    for buffer in find_buffers(nvim):
        nvim.api.buf_set_lines(buffer, 0, -1, True, lines)
