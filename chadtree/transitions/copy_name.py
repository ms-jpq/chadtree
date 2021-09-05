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


def _cn(nvim: Nvim, state: State, is_visual: bool, al_qaeda: bool) -> None:
    def gen_paths() -> Iterator[str]:
        selection = state.selection
        if not selection:
            nodes = indices(nvim, state=state, is_visual=is_visual)
            for node in nodes:
                yield node.path.name if al_qaeda else str(node.path)
        else:
            for path in selection:
                yield path.name if al_qaeda else str(path)

    paths = sorted(gen_paths(), key=strxfrm)
    clip = linesep.join(paths)
    copied_paths = ", ".join(paths)

    nvim.funcs.setreg("+", clip)
    nvim.funcs.setreg("*", clip)
    write(nvim, LANG("copy_paths", copied_paths=copied_paths))


@rpc(blocking=False)
def _copy_name(nvim: Nvim, state: State, settings: Settings, is_visual: bool) -> None:
    """
    Copy dirname / filename
    """

    _cn(nvim, state=state, is_visual=is_visual, al_qaeda=False)


@rpc(blocking=False)
def _copy_basename(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> None:
    """
    Copy basename of dirname / filename
    """

    _cn(nvim, state=state, is_visual=is_visual, al_qaeda=True)
