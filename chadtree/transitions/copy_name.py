from locale import strxfrm
from os import linesep
from typing import Iterator

from pynvim import Nvim
from pynvim_pp.lib import s_write

from ..registry import rpc
from ..settings.localization import LANG
from ..settings.types import Settings
from .shared.index import indices
from ..state.types import State


@rpc(blocking=False)
def _copy_name(nvim: Nvim, state: State, settings: Settings, is_visual: bool) -> None:
    """
    Copy dirname / filename
    """

    def gen_paths() -> Iterator[str]:
        selection = state.selection
        if is_visual or not selection:
            nodes = indices(nvim, state=state, is_visual=is_visual)
            for node in nodes:
                yield node.path
        else:
            for selected in sorted(selection, key=strxfrm):
                yield selected

    paths = tuple(path for path in gen_paths())

    clip = linesep.join(paths)
    copied_paths = ", ".join(paths)

    nvim.funcs.setreg("+", clip)
    nvim.funcs.setreg("*", clip)
    s_write(nvim, LANG("copy_paths", copied_paths=copied_paths))
