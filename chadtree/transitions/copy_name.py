from locale import strxfrm
from os import linesep
from typing import Iterator

from pynvim import Nvim
from pynvim_pp.lib import write

from ..registry import rpc
from ..settings.localization import LANG
from ..settings.types import Settings
from ..state.types import State
from .shared.index import indices


@rpc(blocking=False)
def _copy_name(nvim: Nvim, state: State, settings: Settings, is_visual: bool) -> None:
    """
    Copy dirname / filename
    """

    def gen_paths() -> Iterator[str]:
        selection = state.selection
        if not selection:
            nodes = indices(nvim, state=state, is_visual=is_visual)
            for node in nodes:
                yield node.path
        else:
            yield from selection

    paths = sorted(gen_paths(), key=strxfrm)
    clip = linesep.join(paths)
    copied_paths = ", ".join(paths)

    nvim.funcs.setreg("+", clip)
    nvim.funcs.setreg("*", clip)
    write(nvim, LANG("copy_paths", copied_paths=copied_paths))
