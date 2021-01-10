from mimetypes import guess_type
from os import linesep
from os.path import basename, splitext
from typing import Optional

from pynvim import Nvim

from .wm import show_file
from ...settings.localization import LANG
from ...settings.types import Settings
from ...state.next import forward

from ...state.types import State
from ..types import Stage, State, ClickType


def open_file(
    nvim: Nvim, state: State, settings: Settings, path: str, click_type: ClickType
) -> Optional[Stage]:
    name = basename(path)
    mime, _ = guess_type(name, strict=False)
    m_type, _, _ = (mime or "").partition("/")
    _, ext = splitext(name)

    def ask() -> bool:
        question = LANG("mime_warn", name=name, mime=str(mime))
        resp: int = nvim.funcs.confirm(question, LANG("ask_yesno", linesep=linesep), 2)
        return resp == 1

    go = (
        ask()
        if m_type in settings.mime.warn and ext not in settings.mime.ignore_exts
        else True
    )

    if go:
        new_state = forward(state, settings=settings, current=path)
        show_file(nvim, state=new_state, settings=settings, click_type=click_type)
        return Stage(new_state)
    else:
        return None