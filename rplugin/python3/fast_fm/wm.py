from typing import Iterator, Optional, Sequence, Iterable, Tuple

from .consts import fm_filetype
from .fs import is_parent
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
    w = (
        window
        for window in windows
        if not nvim.api.win_get_option(window, "previewwindow")
    )

    return sorted(w, key=key_by)


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


def new_fm_buffer(nvim: Nvim) -> Buffer:
    buffer: Buffer = nvim.api.create_buf(False, True)
    nvim.api.buf_set_option(buffer, "modifiable", False)
    nvim.api.buf_set_option(buffer, "filetype", fm_filetype)
    return buffer


def new_window(nvim: Nvim, *, open_left: bool) -> Window:
    split = nvim.api.get_option("splitright")

    windows: Sequence[Window] = find_windows_in_tab(nvim)
    focus_win = windows[0] if open_left else windows[-1]
    direction = False if open_left else True
    nvim.api.set_option("splitright", direction)

    nvim.api.set_current_win(focus_win)
    nvim.command("vnew")
    nvim.api.set_option("splitright", split)

    window: Window = nvim.api.get_current_win()
    return window


def resize_fm_windows(nvim: Nvim, *, settings: Settings) -> None:
    for window in find_fm_windows_in_tab(nvim):
        nvim.api.win_set_width(window, settings.width)


def toggle_shown(nvim: Nvim, *, settings: Settings) -> None:
    window: Optional[Window] = next(find_fm_windows_in_tab(nvim), None)
    if window:
        nvim.api.win_close(window, True)
    else:
        buffer: Buffer = next(find_fm_buffers(nvim), None) or new_fm_buffer(nvim)
        window = new_window(nvim, open_left=settings.open_left)
        nvim.api.win_set_buf(window, buffer)
        nvim.api.win_set_option(window, "number", False)
        nvim.api.win_set_option(window, "signcolumn", "no")
        nvim.api.win_set_option(window, "cursorline", True)
        resize_fm_windows(nvim, settings=settings)


def show_file(nvim: Nvim, *, settings: Settings, file: str) -> None:
    buffer: Optional[Buffer] = next(find_buffer_with_file(nvim, file=file), None)
    window: Window = next(find_window_with_file_in_tab(nvim, file=file), None) or next(
        find_non_fm_windows_in_tab(nvim), None
    ) or new_window(nvim, open_left=not settings.open_left)
    nvim.api.set_current_win(window)
    if buffer:
        nvim.api.win_set_buf(window, buffer)
    else:
        nvim.command(f"edit {file}")
    resize_fm_windows(nvim, settings=settings)


def update_buffers(nvim: Nvim, lines: Sequence[str]) -> None:

    for buffer in find_fm_buffers(nvim):
        modifiable = nvim.api.buf_get_option(buffer, "modifiable")
        nvim.api.buf_set_option(buffer, "modifiable", True)
        nvim.api.buf_set_lines(buffer, 0, -1, True, lines)
        nvim.api.buf_set_option(buffer, "modifiable", modifiable)


def kill_buffers(nvim: Nvim, paths: Iterable[str]) -> None:
    buffers: Sequence[Buffer] = nvim.api.list_bufs()
    for buffer in buffers:
        name = nvim.api.buf_get_name(buffer)
        if any(is_parent(parent=path, child=name) for path in paths):
            nvim.command(f"bwipeout! {buffer.number}")
