from contextlib import nullcontext
from itertools import chain
from mimetypes import guess_type
from os.path import altsep, normcase, sep
from pathlib import PurePath
from typing import Optional

from pynvim import Nvim
from pynvim_pp.api import (
    ask_mc,
    buf_set_option,
    cur_buf,
    cur_win,
    set_cur_win,
    win_set_buf,
    win_set_option,
)
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
        win = cur_win(nvim)
        for key, val in settings.win_actual_opts.items():
            win_set_option(nvim, win=win, key=key, val=val)

    path = state.current
    if path:
        hold = click_type is ClickType.secondary
        mgr = hold_win_pos(nvim) if hold else nullcontext()
        with mgr:
            non_fm_windows = tuple(
                find_non_fm_windows_in_tab(nvim, last_used=state.window_order)
            )
            buf = next(find_buffers_with_file(nvim, file=path), None)
            win = next(
                chain(
                    find_window_with_file_in_tab(
                        nvim, last_used=state.window_order, file=path
                    ),
                    non_fm_windows,
                ),
                None,
            ) or new_window(
                nvim,
                last_used=state.window_order,
                win_local=settings.win_actual_opts,
                open_left=not settings.open_left,
                width=None
                if len(non_fm_windows)
                else nvim.options["columns"] - state.width - 1,
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
                escaped = nvim.funcs.fnameescape(normcase(path))
                nvim.command(f"edit! {escaped}")
            else:
                win_set_buf(nvim, win=win, buf=buf)

            resize_fm_windows(nvim, last_used=state.window_order, width=state.width)
            nvim.api.command("filetype detect")


def open_file(
    nvim: Nvim, state: State, settings: Settings, path: PurePath, click_type: ClickType
) -> Optional[Stage]:
    mime, _ = guess_type(path.name, strict=False)
    m_type, _, _ = (mime or "").partition(altsep or sep)

    question = LANG("mime_warn", name=path.name, mime=str(mime))

    go = (
        ask_mc(
            nvim,
            question=question,
            answers=LANG("ask_yesno"),
            answer_key={1: True, 2: False},
        )
        if m_type in settings.mime.warn and path.suffix not in settings.mime.allow_exts
        else True
    )

    if go:
        new_state = forward(state, settings=settings, current=path)
        _show_file(nvim, state=new_state, settings=settings, click_type=click_type)
        return Stage(new_state, focus=path)
    else:
        return None
