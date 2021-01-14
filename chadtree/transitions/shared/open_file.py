from contextlib import nullcontext
from mimetypes import guess_type
from os import linesep
from os.path import basename, splitext
from typing import Optional

from pynvim import Nvim
from pynvim_pp.api import buf_set_option, cur_buf, cur_win, set_cur_win, win_set_buf
from pynvim_pp.hold import hold_win_pos

from ...settings.localization import LANG
from ...settings.types import Settings
from ...state.next import forward
from ...state.types import State
from ..types import ClickType, Stage, State
from .wm import (
    find_buffers_with_file,
    find_non_fm_windows_in_tab,
    find_window_with_file_in_tab,
    new_window,
    resize_fm_windows,
)


def _show_file(
    nvim: Nvim, *, state: State, settings: Settings, click_type: ClickType
) -> None:
    if click_type is ClickType.tertiary:
        nvim.api.command("tabnew")

    path = state.current
    if path:
        hold = click_type is ClickType.secondary
        mgr = hold_win_pos(nvim) if hold else nullcontext()
        with mgr:
            non_fm_windows = tuple(find_non_fm_windows_in_tab(nvim))
            buf = next(find_buffers_with_file(nvim, file=path), None)
            win = (
                next(find_window_with_file_in_tab(nvim, file=path), None)
                or next(iter(non_fm_windows), None)
                or new_window(nvim, open_left=not settings.open_left, width=state.width)
            )

            set_cur_win(nvim, win=win)
            non_fm_count = len(non_fm_windows)

            if click_type is ClickType.v_split and non_fm_count:
                nvim.api.command("vnew")
                temp_buf = cur_buf(nvim)
                buf_set_option(nvim, buf=temp_buf, key="bufhidden", val="wipe")
            elif click_type is ClickType.h_split and non_fm_count:
                nvim.api.command("new")
                temp_buf = cur_buf(nvim)
                buf_set_option(nvim, buf=temp_buf, key="bufhidden", val="wipe")

            win = cur_win(nvim)

            if buf is None:
                nvim.command(f"edit {path}")
            else:
                win_set_buf(nvim, win=win, buf=buf)

            resize_fm_windows(nvim, state.width)
            nvim.api.command("filetype detect")


def open_file(
    nvim: Nvim, state: State, settings: Settings, path: str, click_type: ClickType
) -> Optional[Stage]:
    name = basename(path)
    mime, _ = guess_type(name, strict=False)
    m_type, _, _ = (mime or "").partition("/")
    _, ext = splitext(name)

    def ask() -> bool:
        question = LANG("mime_warn", name=name, mime=str(mime))
        resp: int = nvim.funcs.confirm(question, LANG("ask_yesno"), 2)
        return resp == 1

    go = (
        ask()
        if m_type in settings.mime.warn and ext not in settings.mime.ignore_exts
        else True
    )

    if go:
        new_state = forward(state, settings=settings, current=path)
        _show_file(nvim, state=new_state, settings=settings, click_type=click_type)
        return Stage(new_state)
    else:
        return None
