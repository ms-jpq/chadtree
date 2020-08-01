from typing import Any, Dict, Iterable, Iterator, Optional, Sequence, Tuple, cast

from pynvim import Nvim
from pynvim.api.buffer import Buffer
from pynvim.api.tabpage import Tabpage
from pynvim.api.window import Window

from .consts import fm_filetype, fm_namespace
from .fs import is_parent
from .nvim import atomic
from .types import Badge, Highlight, Render, Settings, State


def is_fm_buffer(nvim: Nvim, buffer: Buffer) -> bool:
    ft = nvim.api.buf_get_option(buffer, "filetype")
    return ft == fm_filetype


def find_windows_in_tab(nvim: Nvim) -> Iterator[Window]:
    def key_by(window: Window) -> Tuple[int, int]:
        row, col = nvim.api.win_get_position(window)
        return (col, row)

    tab: Tabpage = nvim.api.get_current_tabpage()
    windows: Sequence[Window] = nvim.api.tabpage_list_wins(tab)

    for window in sorted(windows, key=key_by):
        if not nvim.api.win_get_option(window, "previewwindow"):
            yield window


def find_fm_windows(nvim: Nvim) -> Iterator[Tuple[Window, Buffer]]:
    for window in nvim.api.list_wins():
        buffer: Buffer = nvim.api.win_get_buf(window)
        if is_fm_buffer(nvim, buffer=buffer):
            yield window, buffer


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


def find_current_buffer_name(nvim: Nvim) -> str:
    buffer = nvim.api.get_current_buf()
    name = nvim.api.buf_get_name(buffer)
    return name


def new_fm_buffer(nvim: Nvim, keymap: Dict[str, Sequence[str]]) -> Buffer:
    options = {"noremap": True, "silent": True, "nowait": True}
    buffer: Buffer = nvim.api.create_buf(False, True)
    nvim.api.buf_set_option(buffer, "modifiable", False)
    nvim.api.buf_set_option(buffer, "filetype", fm_filetype)

    for function, mappings in keymap.items():
        for mapping in mappings:
            nvim.api.buf_set_keymap(
                buffer, "n", mapping, f"<cmd>call {function}(v:false)<cr>", options
            )
            nvim.api.buf_set_keymap(
                buffer, "v", mapping, f"<esc><cmd>call {function}(v:true)<cr>", options,
            )
    return buffer


def new_window(nvim: Nvim, *, open_left: bool) -> Window:
    split_b = nvim.api.get_option("splitbelow")
    split_r = nvim.api.get_option("splitright")

    windows: Sequence[Window] = tuple(w for w in find_windows_in_tab(nvim))
    focus_win = windows[0] if open_left else windows[-1]
    direction = False if open_left else True

    nvim.api.set_option("splitbelow", True)
    nvim.api.set_option("splitright", direction)
    nvim.api.set_current_win(focus_win)
    nvim.command("vnew")
    nvim.api.set_option("splitbelow", split_b)
    nvim.api.set_option("splitright", split_r)

    window: Window = nvim.api.get_current_win()
    return window


def resize_fm_windows(nvim: Nvim, width: int) -> None:
    for window in find_fm_windows_in_tab(nvim):
        nvim.api.win_set_width(window, width)


def kill_fm_windows(nvim: Nvim, *, settings: Settings) -> None:
    for window in find_fm_windows_in_tab(nvim):
        nvim.api.win_close(window, True)


def toggle_fm_window(nvim: Nvim, *, state: State, settings: Settings) -> None:
    window: Optional[Window] = next(find_fm_windows_in_tab(nvim), None)
    if window:
        nvim.api.win_close(window, True)
    else:
        buffer: Buffer = next(find_fm_buffers(nvim), None)
        if buffer is None:
            buffer = new_fm_buffer(nvim, keymap=settings.keymap)
        window = new_window(nvim, open_left=settings.open_left)
        nvim.api.win_set_buf(window, buffer)
        nvim.api.command("setlocal nonumber")
        nvim.api.command("setlocal nowrap")
        nvim.api.command("setlocal signcolumn=no")
        nvim.api.command("setlocal cursorline")
        nvim.api.command("setlocal winfixwidth")
        resize_fm_windows(nvim, state.width)


def show_file(nvim: Nvim, *, state: State, settings: Settings) -> None:
    path = state.current
    if path:
        buffer: Optional[Buffer] = next(find_buffer_with_file(nvim, file=path), None)
        window: Window = next(
            find_window_with_file_in_tab(nvim, file=path), None
        ) or next(find_non_fm_windows_in_tab(nvim), None) or new_window(
            nvim, open_left=not settings.open_left
        )

        nvim.api.set_current_win(window)
        if buffer is None:
            nvim.command(f"edit {path}")
        else:
            nvim.api.win_set_buf(window, buffer)
        resize_fm_windows(nvim, width=state.width)
        nvim.api.command("filetype detect")


def kill_buffers(nvim: Nvim, paths: Iterable[str]) -> None:
    buffers: Sequence[Buffer] = nvim.api.list_bufs()
    for buffer in buffers:
        name = nvim.api.buf_get_name(buffer)
        if any(name == path or is_parent(parent=path, child=name) for path in paths):
            nvim.command(f"bwipeout! {buffer.number}")


def buf_setlines(
    nvim: Nvim, buffer: Buffer, lines: Sequence[str]
) -> Iterator[Tuple[str, Sequence[Any]]]:
    yield "buf_set_option", (buffer, "modifiable", True)
    yield "buf_set_lines", (buffer, 0, -1, True, lines)
    yield "buf_set_option", (buffer, "modifiable", False)


def buf_set_virtualtext(
    nvim: Nvim, buffer: Buffer, ns: int, vtext: Sequence[Sequence[Badge]]
) -> Iterator[Tuple[str, Sequence[Any]]]:
    for idx, badges in enumerate(vtext):
        vtxt = tuple((badge.text, badge.group) for badge in badges)
        yield "buf_set_virtual_text", (
            buffer,
            ns,
            idx,
            vtxt,
            {},
        )


def buf_set_highlights(
    nvim: Nvim, buffer: Buffer, ns: int, highlights: Sequence[Sequence[Highlight]]
) -> Iterator[Tuple[str, Sequence[Any]]]:
    for idx, hl in enumerate(highlights):
        for h in hl:
            yield "buf_add_highlight", (buffer, ns, h.group, idx, h.begin, h.end)


def update_buffers(nvim: Nvim, rendering: Sequence[Render]) -> None:
    lines, badges, highlights = tuple(
        zip(*((render.line, render.badges, render.highlights) for render in rendering))
    )
    ns = nvim.api.create_namespace(fm_namespace)

    for window, buffer in find_fm_windows(nvim):
        row, col = nvim.api.win_get_cursor(window)
        lines = cast(Sequence[str], lines)
        new_row = min(row, len(lines))
        it1 = "buf_clear_namespace", (buffer, ns, 0, -1)
        it2 = buf_setlines(nvim, buffer=buffer, lines=lines)
        it3 = buf_set_virtualtext(
            nvim, buffer=buffer, ns=ns, vtext=cast(Sequence[Sequence[Badge]], badges),
        )
        it4 = buf_set_highlights(
            nvim,
            buffer=buffer,
            ns=ns,
            highlights=cast(Sequence[Sequence[Highlight]], highlights),
        )
        it5 = "win_set_cursor", (window, (new_row, col))
        atomic(
            nvim, it1, *it2, *it3, *it4, it5,
        )
