from locale import strxfrm
from os import linesep
from os.path import normpath
from pathlib import PurePath
from typing import Callable, Iterator

from pynvim import Nvim
from pynvim_pp.lib import write

from ..registry import rpc
from ..settings.localization import LANG
from ..settings.types import Settings
from ..state.types import State
from .shared.index import indices


def _cn(
    nvim: Nvim, state: State, is_visual: bool, proc: Callable[[PurePath], str]
) -> None:
    def gen_paths() -> Iterator[str]:
        selection = state.selection
        if not selection:
            nodes = indices(nvim, state=state, is_visual=is_visual)
            for node in nodes:
                yield proc(node.path)
        else:
            for path in selection:
                yield proc(path)

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

    _cn(
        nvim,
        state=state,
        is_visual=is_visual,
        proc=lambda p: normpath(p.name),
    )


@rpc(blocking=False)
def _copy_basename(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> None:
    """
    Copy basename of dirname / filename
    """

    _cn(
        nvim,
        state=state,
        is_visual=is_visual,
        proc=normpath,
    )


@rpc(blocking=False)
def _copy_relname(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> None:
    """
    Copy relname of dirname / filename
    """

    _cn(
        nvim,
        state=state,
        is_visual=is_visual,
        proc=lambda p: normpath(p.relative_to(state.root.path)),
    )
