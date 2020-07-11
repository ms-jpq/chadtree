from typing import Iterator, Optional, Sequence, Tuple

from .consts import fm_filetype
from .nvim import Buffer, Nvim, Tabpage, Window
from .types import Settings


def is_fm_buffer(nvim: Nvim, buffer: Buffer) -> bool:
    ft = nvim.api.buf_get_option(buffer, "filetype")
    return ft == fm_filetype


def find_windows_in_tab(nvim: Nvim) -> Sequence[Window]:
    def key_by(window: Window) -> Tuple[int, int]:
        row, col = nvim.api.win_get_position(window)
        return (col, row)

    tab: Tabpage = nvim.api.get_current_tabpage()
    windows: Sequence[Window] = nvim.api.tabpage_list_wins(tab)

    return sorted(windows, key=key_by)


def find_fm_windows_in_tab(nvim: Nvim) -> Iterator[Window]:
    for window in find_windows_in_tab(nvim):
        buffer: Buffer = nvim.api.win_get_buf(window)
        if is_fm_buffer(nvim, buffer=buffer):
            yield window


def find_non_fm_windows_in_tab(nvim: Nvim) -> Iterator[Window]:
    for window in find_windows_in_tab(nvim):
        buffer: Buffer = nvim.api.win_get_buf(window)
        if not is_fm_buffer(nvim, buffer=buffer):
            yield window


def find_window_with_file_in_tab(nvim: Nvim, file: str) -> Iterator[Window]:
    for window in find_windows_in_tab(nvim):
        buffer: Buffer = nvim.api.win_get_buf(window)
        name = nvim.api.buf_get_name(buffer)
        if name == file:
            yield window


def find_fm_buffers(nvim: Nvim) -> Iterator[Buffer]:
    buffers: Sequence[Buffer] = nvim.api.list_bufs()
    for buffer in buffers:
        if is_fm_buffer(nvim, buffer=buffer):
            yield buffer


def find_buffer_with_file(nvim: Nvim, file: str) -> Iterator[Buffer]:
    buffers: Sequence[Buffer] = nvim.api.list_bufs()
    for buffer in buffers:
        name = nvim.api.buf_get_name(buffer)
        if name == file:
            yield buffer


def new_buffer_with_file(nvim: Nvim, file: str) -> Buffer:
    buffer: Buffer = nvim.api.create_buf(False, True)
    return buffer


def new_fm_buffer(nvim: Nvim) -> Buffer:
    buffer: Buffer = nvim.api.create_buf(False, True)
    nvim.api.buf_set_option(buffer, "modifiable", False)
    nvim.api.buf_set_option(buffer, "filetype", fm_filetype)
    return buffer


def new_window(nvim: Nvim, buffer: Buffer) -> Window:
    nvim.command("vnew")
    window: Window = nvim.api.get_current_win()
    nvim.api.win_set_buf(window, buffer)
    return window


def toggle_shown(nvim: Nvim, settings: Settings) -> None:
    window: Optional[Window] = next(find_fm_windows_in_tab(nvim), None)
    if window:
        nvim.api.win_close(window, True)
    else:
        buffer: Buffer = next(find_fm_buffers(nvim), None) or new_fm_buffer(nvim)
        window = new_window(nvim, buffer=buffer)
        nvim.api.win_set_width(window, settings.width)


def show_file(nvim: Nvim, file: str) -> None:
    buffer: Buffer = next(
        find_buffer_with_file(nvim, file=file), None
    ) or new_buffer_with_file(nvim, file=file)
    window: Window = next(find_window_with_file_in_tab(nvim, file=file), None) or next(
        find_non_fm_windows_in_tab(nvim), None
    ) or new_window(nvim, buffer)

    nvim.api.win_set_buf(window, buffer)
    nvim.api.set_current_win(window)


def update_buffers(nvim: Nvim, lines: Sequence[str]) -> None:

    for buffer in find_fm_buffers(nvim):
        nvim.api.buf_set_option(buffer, "modifiable", True)
        nvim.api.buf_set_lines(buffer, 0, -1, True, lines)
        nvim.api.buf_set_option(buffer, "modifiable", False)
