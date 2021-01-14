from typing import AbstractSet, Iterator, Mapping, Sequence, Tuple

from pynvim import Nvim
from pynvim.api.buffer import Buffer
from pynvim.api.tabpage import Tabpage
from pynvim.api.window import Window
from pynvim_pp.keymap import Keymap

from ...consts import FM_FILETYPE
from ...fs.ops import ancestors


def is_fm_buffer(nvim: Nvim, buffer: Buffer) -> bool:
    ft: str = nvim.api.buf_get_option(buffer, "filetype")
    return ft == FM_FILETYPE


def find_windows_in_tab(nvim: Nvim, no_preview: bool) -> Iterator[Window]:
    def key_by(window: Window) -> Tuple[int, int]:
        """
        -> sort by row, then col
        """

        row, col = nvim.api.win_get_position(window)
        return col, row

    tab: Tabpage = nvim.api.get_current_tabpage()
    windows: Sequence[Window] = nvim.api.tabpage_list_wins(tab)

    for window in sorted(windows, key=key_by):
        if not no_preview or not nvim.api.win_get_option(window, "previewwindow"):
            yield window


def find_fm_windows(nvim: Nvim) -> Iterator[Tuple[Window, Buffer]]:
    for window in nvim.api.list_wins():
        buffer: Buffer = nvim.api.win_get_buf(window)
        if is_fm_buffer(nvim, buffer=buffer):
            yield window, buffer


def find_fm_windows_in_tab(nvim: Nvim) -> Iterator[Window]:
    for window in find_windows_in_tab(nvim, no_preview=True):
        buffer: Buffer = nvim.api.win_get_buf(window)
        if is_fm_buffer(nvim, buffer=buffer):
            yield window


def find_non_fm_windows_in_tab(nvim: Nvim) -> Iterator[Window]:
    for window in find_windows_in_tab(nvim, no_preview=True):
        buffer: Buffer = nvim.api.win_get_buf(window)
        if not is_fm_buffer(nvim, buffer=buffer):
            yield window


def find_window_with_file_in_tab(nvim: Nvim, file: str) -> Iterator[Window]:
    for window in find_windows_in_tab(nvim, no_preview=True):
        buffer: Buffer = nvim.api.win_get_buf(window)
        name = nvim.api.buf_get_name(buffer)
        if name == file:
            yield window


def find_fm_buffers(nvim: Nvim) -> Iterator[Buffer]:
    buffers: Sequence[Buffer] = nvim.api.list_bufs()
    for buffer in buffers:
        if is_fm_buffer(nvim, buffer=buffer):
            yield buffer


def find_buffers_with_file(nvim: Nvim, file: str) -> Iterator[Buffer]:
    buffers: Sequence[Buffer] = nvim.api.list_bufs()
    for buffer in buffers:
        name = nvim.api.buf_get_name(buffer)
        if name == file:
            yield buffer


def find_current_buffer_name(nvim: Nvim) -> str:
    buffer: Buffer = nvim.api.get_current_buf()
    name: str = nvim.api.buf_get_name(buffer)
    return name


def new_fm_buffer(nvim: Nvim, keymap: Mapping[str, AbstractSet[str]]) -> Buffer:
    buffer: Buffer = nvim.api.create_buf(False, True)
    nvim.api.buf_set_option(buffer, "modifiable", False)
    nvim.api.buf_set_option(buffer, "filetype", FM_FILETYPE)

    km = Keymap()
    for function, mappings in keymap.items():
        for mapping in mappings:
            km.n(
                mapping, noremap=True, silent=True, nowait=True
            ) << f"<cmd>lua {function}(false)<cr>"
            km.v(
                mapping, noremap=True, silent=True, nowait=True
            ) << f"<cmd>lua {function}(true)<cr>"

    km.drain(buf=buffer).commit(nvim)
    return buffer


def new_window(nvim: Nvim, *, open_left: bool, width: int) -> Window:
    split_r = nvim.api.get_option("splitright")

    windows = tuple(w for w in find_windows_in_tab(nvim, no_preview=False))
    focus_win = windows[0] if open_left else windows[-1]
    direction = False if open_left else True

    nvim.api.set_option("splitright", direction)
    nvim.api.set_current_win(focus_win)
    nvim.command(f"{width}vsplit")
    nvim.api.set_option("splitright", split_r)

    window: Window = nvim.api.get_current_win()
    return window


def resize_fm_windows(nvim: Nvim, width: int) -> None:
    for window in find_fm_windows_in_tab(nvim):
        nvim.api.win_set_width(window, width)


def kill_buffers(nvim: Nvim, paths: AbstractSet[str]) -> None:
    buffers: Sequence[Buffer] = nvim.api.list_bufs()
    for buffer in buffers:
        buf_name = nvim.api.buf_get_name(buffer)
        buf_paths = ancestors(buf_name) | {buf_name}
        if buf_paths & paths:
            nvim.api.buf_delete(buffer, {"force": True})
