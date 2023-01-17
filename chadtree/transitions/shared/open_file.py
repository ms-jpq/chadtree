from mimetypes import guess_type
from os.path import altsep, normpath, sep
from pathlib import PurePath
from typing import AsyncContextManager, Optional, cast

from pynvim_pp.buffer import Buffer
from pynvim_pp.hold import hold_win
from pynvim_pp.logging import log
from pynvim_pp.nvim import Nvim
from pynvim_pp.types import NvimError
from pynvim_pp.window import Window
from std2 import anext
from std2.aitertools import achain, to_async
from std2.contextlib import nullacontext

from ...settings.localization import LANG
from ...settings.types import Settings
from ...state.next import forward
from ...state.types import State
from ..types import ClickType, Stage
from .wm import (
    find_buffers_with_file,
    find_non_fm_windows_in_tab,
    find_window_with_file_in_tab,
    new_window,
    resize_fm_windows,
)


async def _show_file(
    *, state: State, settings: Settings, click_type: ClickType
) -> None:
    if click_type is ClickType.tertiary:
        await Nvim.exec("tabnew")
        win = await Window.get_current()
        for key, val in settings.win_actual_opts.items():
            await win.opts.set(key, val=val)

    path = state.current
    if path:
        hold = click_type is ClickType.secondary
        mgr = (
            cast(AsyncContextManager[None], hold_win(win=None))
            if hold
            else nullacontext(None)
        )
        async with mgr:
            non_fm_windows = [
                win
                async for win in find_non_fm_windows_in_tab(
                    last_used=state.window_order
                )
            ]
            buf = await anext(find_buffers_with_file(file=path), None)
            win = await anext(
                achain(
                    find_window_with_file_in_tab(
                        last_used=state.window_order, file=path
                    ),
                    to_async(non_fm_windows),
                ),
                cast(Window, None),
            ) or await new_window(
                last_used=state.window_order,
                win_local=settings.win_actual_opts,
                open_left=not settings.open_left,
                width=None
                if len(non_fm_windows)
                else await Nvim.opts.get(int, "columns") - state.width - 1,
            )

            await Window.set_current(win)
            non_fm_count = len(non_fm_windows)

            if click_type is ClickType.v_split and non_fm_count:
                await Nvim.exec("vnew")
                temp_buf = await Buffer.get_current()
                await temp_buf.opts.set("bufhidden", val="wipe")
            elif click_type is ClickType.h_split and non_fm_count:
                await Nvim.exec("new")
                temp_buf = await Buffer.get_current()
                await temp_buf.opts.set("bufhidden", val="wipe")

            win = await Window.get_current()

            if buf is None:
                escaped = await Nvim.fn.fnameescape(str, normpath(path))
                await Nvim.exec(f"edit! {escaped}")
            else:
                await win.set_buf(buf)

            await resize_fm_windows(last_used=state.window_order, width=state.width)
            try:
                await Nvim.exec("filetype detect")
            except NvimError as e:
                log.warn("%s", e)


async def open_file(
    state: State, settings: Settings, path: PurePath, click_type: ClickType
) -> Optional[Stage]:
    mime, _ = guess_type(path.name, strict=False)
    m_type, _, _ = (mime or "").partition(altsep or sep)

    question = LANG("mime_warn", name=path.name, mime=str(mime))

    go = (
        await Nvim.confirm(
            question=question,
            answers=LANG("ask_yesno"),
            answer_key={1: True, 2: False},
        )
        if m_type in settings.mime.warn and path.suffix not in settings.mime.allow_exts
        else True
    )

    if go:
        new_state = await forward(state, settings=settings, current=path)
        await _show_file(state=new_state, settings=settings, click_type=click_type)
        return Stage(new_state, focus=path)
    else:
        return None
