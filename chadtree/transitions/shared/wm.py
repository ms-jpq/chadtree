from typing import AbstractSet, Iterator, Mapping, Optional, Tuple, Union

from pynvim.api import Buffer, Nvim, Window
from pynvim_pp.api import (
    buf_close,
    buf_filetype,
    buf_name,
    buf_set_option,
    create_buf,
    cur_buf,
    cur_tab,
    cur_win,
    list_bufs,
    list_wins,
    set_cur_win,
    tab_list_wins,
    win_get_buf,
    win_get_option,
    win_set_option,
)
from pynvim_pp.keymap import Keymap

from ...consts import FM_FILETYPE
from ...fs.ops import ancestors
from ...settings.types import Settings


def is_fm_buffer(nvim: Nvim, buf: Buffer) -> bool:
    ft = buf_filetype(nvim, buf=buf)
    return ft == FM_FILETYPE


def is_fm_window(nvim: Nvim, win: Window) -> bool:
    buf = win_get_buf(nvim, win=win)
    return is_fm_buffer(nvim, buf=buf)


def find_windows_in_tab(nvim: Nvim, no_secondary: bool) -> Iterator[Window]:
    def key_by(win: Window) -> Tuple[int, int]:
        """
        -> sort by row, then col
        """

        row, col = nvim.funcs.win_screenpos(win.number)
        return col, row

    tab = cur_tab(nvim)
    wins = tab_list_wins(nvim, tab=tab)

    for win in sorted(wins, key=key_by):
        is_preview: bool = win_get_option(nvim, win=win, key="previewwindow")
        buf = win_get_buf(nvim, win)
        ft = buf_filetype(nvim, buf=buf)
        is_secondary = is_preview or ft == "qf"
        if not is_secondary or not no_secondary:
            yield win


def find_fm_windows(nvim: Nvim) -> Iterator[Tuple[Window, Buffer]]:
    for win in list_wins(nvim):
        buf = win_get_buf(nvim, win=win)
        if is_fm_buffer(nvim, buf=buf):
            yield win, buf


def find_fm_windows_in_tab(nvim: Nvim) -> Iterator[Window]:
    for win in find_windows_in_tab(nvim, no_secondary=True):
        buf = win_get_buf(nvim, win=win)
        if is_fm_buffer(nvim, buf=buf):
            yield win


def find_non_fm_windows_in_tab(nvim: Nvim) -> Iterator[Window]:
    for win in find_windows_in_tab(nvim, no_secondary=True):
        buf = win_get_buf(nvim, win=win)
        if not is_fm_buffer(nvim, buf=buf):
            yield win


def find_window_with_file_in_tab(nvim: Nvim, file: str) -> Iterator[Window]:
    for win in find_windows_in_tab(nvim, no_secondary=True):
        buf = win_get_buf(nvim, win=win)
        name = buf_name(nvim, buf=buf)
        if name == file:
            yield win


def find_fm_buffers(nvim: Nvim) -> Iterator[Buffer]:
    for buf in list_bufs(nvim, listed=True):
        if is_fm_buffer(nvim, buf=buf):
            yield buf


def find_buffers_with_file(nvim: Nvim, file: str) -> Iterator[Buffer]:
    for buf in list_bufs(nvim, listed=True):
        name = buf_name(nvim, buf=buf)
        if name == file:
            yield buf


def find_current_buffer_name(nvim: Nvim) -> str:
    buf = cur_buf(nvim)
    name = buf_name(nvim, buf=buf)
    return name


def new_fm_buffer(nvim: Nvim, settings: Settings) -> Buffer:
    buf = create_buf(
        nvim, listed=False, scratch=True, wipe=False, nofile=True, noswap=True
    )
    buf_set_option(nvim, buf=buf, key="modifiable", val=False)
    buf_set_option(nvim, buf=buf, key="filetype", val=FM_FILETYPE)

    km = Keymap()
    km.n("{") << f"{settings.page_increment}<up>"
    km.n("}") << f"{settings.page_increment}<down>"
    for function, mappings in settings.keymap.items():
        for mapping in mappings:
            (
                km.n(mapping, noremap=True, silent=True, nowait=True)
                << f"<cmd>lua {function}(false)<cr>"
            )
            (
                km.v(mapping, noremap=True, silent=True, nowait=True)
                << f"<esc><cmd>lua {function}(true)<cr>"
            )

    km.drain(buf=buf).commit(nvim)
    return buf


def new_window(
    nvim: Nvim,
    *,
    win_local: Mapping[str, Union[bool, str]],
    open_left: bool,
    width: Optional[int],
) -> Window:
    split_r = nvim.options["splitright"]

    wins = tuple(find_windows_in_tab(nvim, no_secondary=False))
    focus_win = wins[0] if open_left else wins[-1]
    direction = False if open_left else True

    nvim.options["splitright"] = direction
    set_cur_win(nvim, win=focus_win)
    nvim.command(f"{width}vnew" if width else "vnew")
    nvim.options["splitright"] = split_r

    win = cur_win(nvim)
    buf = win_get_buf(nvim, win)
    for key, val in win_local.items():
        win_set_option(nvim, win=win, key=key, val=val)
    buf_set_option(nvim, buf=buf, key="bufhidden", val="wipe")
    return win


def resize_fm_windows(nvim: Nvim, width: int) -> None:
    for window in find_fm_windows_in_tab(nvim):
        window.width = width


def kill_buffers(nvim: Nvim, paths: AbstractSet[str]) -> Iterator[Buffer]:
    for buf in list_bufs(nvim, listed=True):
        name = buf_name(nvim, buf=buf)
        buf_paths = ancestors(name) | {name}
        if not buf_paths.isdisjoint(paths):
            buf_close(nvim, buf=buf)
            yield buf

