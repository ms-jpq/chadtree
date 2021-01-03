from typing import Dict, Iterable, Iterator, Optional, Sequence, Tuple, cast

from pynvim import Nvim
from pynvim.api.buffer import Buffer
from pynvim.api.tabpage import Tabpage
from pynvim.api.window import Window
from pynvim_pp.atomic import Atomic
from pynvim_pp.hold import hold_win_pos
from std2.contextlib import nil_manager

from .consts import fm_filetype, fm_namespace
from .fs import is_parent
from .types import Badge, ClickType, Highlight, OpenArgs, Settings, State


def is_fm_buffer(nvim: Nvim, buffer: Buffer) -> bool:
    ft = nvim.api.buf_get_option(buffer, "filetype")
    return ft == fm_filetype


def find_windows_in_tab(nvim: Nvim, exclude: bool) -> Iterator[Window]:
    def key_by(window: Window) -> Tuple[int, int]:
        row, col = nvim.api.win_get_position(window)
        return (col, row)

    tab: Tabpage = nvim.api.get_current_tabpage()
    windows: Sequence[Window] = nvim.api.tabpage_list_wins(tab)

    for window in sorted(windows, key=key_by):
        if not exclude or not nvim.api.win_get_option(window, "previewwindow"):
            yield window


def find_fm_windows(nvim: Nvim) -> Iterator[Tuple[Window, Buffer]]:
    for window in nvim.api.list_wins():
        buffer: Buffer = nvim.api.win_get_buf(window)
        if is_fm_buffer(nvim, buffer=buffer):
            yield window, buffer


def find_fm_windows_in_tab(nvim: Nvim) -> Iterator[Window]:
    for window in find_windows_in_tab(nvim, exclude=True):
        buffer: Buffer = nvim.api.win_get_buf(window)
        if is_fm_buffer(nvim, buffer=buffer):
            yield window


def find_non_fm_windows_in_tab(nvim: Nvim) -> Iterator[Window]:
    for window in find_windows_in_tab(nvim, exclude=True):
        buffer: Buffer = nvim.api.win_get_buf(window)
        if not is_fm_buffer(nvim, buffer=buffer):
            yield window


def find_window_with_file_in_tab(nvim: Nvim, file: str) -> Iterator[Window]:
    for window in find_windows_in_tab(nvim, exclude=True):
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
                buffer,
                "v",
                mapping,
                f"<esc><cmd>call {function}(v:true)<cr>",
                options,
            )
    return buffer


def new_window(nvim: Nvim, *, open_left: bool, width: int) -> Window:
    split_r = nvim.api.get_option("splitright")

    windows: Sequence[Window] = tuple(
        w for w in find_windows_in_tab(nvim, exclude=False)
    )
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


def kill_fm_windows(nvim: Nvim, *, settings: Settings) -> None:
    windows: Sequence[Window] = nvim.api.list_wins()
    if len(windows) <= 1:
        nvim.api.command("quit")
    else:
        for window in find_fm_windows_in_tab(nvim):
            nvim.api.win_close(window, True)


def ensure_side_window(
    nvim: Nvim, *, window: Window, state: State, settings: Settings
) -> None:
    open_left = settings.open_left
    windows = tuple(find_windows_in_tab(nvim, exclude=False))
    target = windows[0] if open_left else windows[-1]
    if window.number != target.number:
        if open_left:
            nvim.api.command("wincmd H")
        else:
            nvim.api.command("wincmd L")
        resize_fm_windows(nvim, state.width)


def toggle_fm_window(
    nvim: Nvim, *, state: State, settings: Settings, opts: OpenArgs
) -> None:
    cwin: Window = nvim.api.get_current_win()
    window: Optional[Window] = next(find_fm_windows_in_tab(nvim), None)
    if window:
        windows: Sequence[Window] = nvim.api.list_wins()
        if len(windows) <= 1:
            pass
        else:
            nvim.api.win_close(window, True)
    else:
        buffer: Optional[Buffer] = next(find_fm_buffers(nvim), None)
        if buffer is None:
            buffer = new_fm_buffer(nvim, keymap=settings.keymap)
        window = new_window(nvim, open_left=settings.open_left, width=state.width)
        nvim.api.win_set_buf(window, buffer)
        for option in settings.win_local_opts:
            nvim.api.win_set_option(window, option)
        ensure_side_window(nvim, window=window, state=state, settings=settings)
        if not opts.focus:
            nvim.api.set_current_win(cwin)


def show_file(
    nvim: Nvim, *, state: State, settings: Settings, click_type: ClickType
) -> None:
    path = state.current
    hold = click_type == ClickType.secondary
    if click_type == ClickType.tertiary:
        nvim.api.command("tabnew")
    if path:
        mgr = hold_win_pos(nvim) if hold else nil_manager()
        with mgr:
            non_fm_windows = tuple(find_non_fm_windows_in_tab(nvim))
            buffer: Optional[Buffer] = next(
                find_buffer_with_file(nvim, file=path), None
            )
            window: Window = (
                next(find_window_with_file_in_tab(nvim, file=path), None)
                or next(iter(non_fm_windows), None)
                or new_window(nvim, open_left=not settings.open_left, width=state.width)
            )

            nvim.api.set_current_win(window)
            non_fm_count = len(non_fm_windows)

            temp_buf: Optional[Buffer] = None

            if click_type == ClickType.v_split and non_fm_count:
                nvim.api.command("vnew")
                temp_buf = nvim.api.get_current_buf()
                nvim.api.buf_set_option(temp_buf, "bufhidden", "wipe")
            elif click_type == ClickType.h_split and non_fm_count:
                nvim.api.command("new")
                temp_buf = nvim.api.get_current_buf()
                nvim.api.buf_set_option(temp_buf, "bufhidden", "wipe")

            window = nvim.api.get_current_win()

            if buffer is None:
                nvim.command(f"edit {path}")
            else:
                nvim.api.win_set_buf(window, buffer)
            resize_fm_windows(nvim, state.width)
            nvim.api.command("filetype detect")


def kill_buffers(nvim: Nvim, paths: Iterable[str]) -> None:
    buffers: Sequence[Buffer] = nvim.api.list_bufs()
    for buffer in buffers:
        name = nvim.api.buf_get_name(buffer)
        if any(name == path or is_parent(parent=path, child=name) for path in paths):
            nvim.command(f"bwipeout! {buffer.number}")


def update_buffers(nvim: Nvim, state: State, focus: Optional[str]) -> None:
    focus_row = state.paths_lookup.get(focus) if focus else None
    current = state.current
    current_row = state.paths_lookup.get(current or "")
    lines, badges, highlights = zip(
        *((render.line, render.badges, render.highlights) for render in state.rendered)
    )
    cwin = nvim.api.get_current_win()
    ns = nvim.api.create_namespace(fm_namespace)

    for window, buffer in find_fm_windows(nvim):
        row, col = nvim.api.win_get_cursor(window)
        new_row = (
            focus_row + 1
            if focus_row is not None
            else (
                current_row + 1
                if window.number != cwin.number and current_row is not None
                else min(row, len(lines))
            )
        )

        atomic = Atomic()
        atomic.buf_clear_namespace(buffer, ns, 0, -1)
        atomic.buf_set_option(buffer, "modifiable", True)
        atomic.buf_set_lines(buffer, 0, -1, True, lines)
        atomic.buf_set_option(buffer, "modifiable", False)

        vtext = cast(Sequence[Sequence[Badge]], badges)
        for idx, badges in enumerate(vtext):
            vtxt = tuple((badge.text, badge.group) for badge in badges)
            atomic.buf_set_virtual_text(buffer, ns, idx, vtxt)

        hl2 = cast(Sequence[Sequence[Highlight]], highlights)
        for idx, hl in enumerate(hl2):
            for h in hl:
                atomic.buf_add_highlight(buffer, ns, h.group, idx, h.begin, h.end)

        atomic.win_set_cursor(window, (new_row, col))
        atomic.commit(nvim)
