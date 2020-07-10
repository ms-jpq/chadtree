from typing import Any, Iterable, Iterator, Sequence, Tuple

from pynvim import Nvim

from .consts import fm_filetype

Tab = Any
Window = Any
Buffer = Any


def sorted_windows(nvim: Nvim, window: Iterable[Window]) -> Sequence[Window]:
    def key_by(window: Window) -> Tuple[int, int]:
        row, col = nvim.api.win_get_position(window)
        return (col, row)

    return sorted(window, key=key_by)


def find(nvim: Nvim) -> Iterator[Tuple[Window, Buffer]]:
    tab = nvim.api.get_current_tabpage()
    windows = nvim.api.tabpage_list_wins(tab)
    for window in sorted_windows(nvim, windows):
        buffer = nvim.api.win_get_buf(window)
        ft = nvim.api.buf_get_option(buffer, "filetype")
        if ft == fm_filetype:
            yield window, buffer


def new() -> None:
    pass


def toggle_shown(nvim: Nvim) -> None:
    pass
