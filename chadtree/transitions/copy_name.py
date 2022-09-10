from locale import strxfrm
from os import linesep
from os.path import normpath
from pathlib import PurePath
from typing import AsyncIterator, Callable

from pynvim_pp.nvim import Nvim
from pynvim_pp.types import NoneType

from ..registry import rpc
from ..settings.localization import LANG
from ..settings.types import Settings
from ..state.types import State
from .shared.index import indices


async def _cn(state: State, is_visual: bool, proc: Callable[[PurePath], str]) -> None:
    async def gen_paths() -> AsyncIterator[str]:
        selection = state.selection
        if not selection:
            nodes = indices(state, is_visual=is_visual)
            async for node in nodes:
                yield proc(node.path)
        else:
            for path in selection:
                yield proc(path)

    paths = sorted([path async for path in gen_paths()], key=strxfrm)
    clip = linesep.join(paths)
    copied_paths = ", ".join(paths)

    await Nvim.fn.setreg(NoneType, "+", clip)
    await Nvim.fn.setreg(NoneType, "*", clip)
    await Nvim.write(LANG("copy_paths", copied_paths=copied_paths))


@rpc(blocking=False)
async def _copy_name(state: State, settings: Settings, is_visual: bool) -> None:
    """
    Copy dirname / filename
    """

    await _cn(
        state,
        is_visual=is_visual,
        proc=lambda p: normpath(p.name),
    )


@rpc(blocking=False)
async def _copy_basename(state: State, settings: Settings, is_visual: bool) -> None:
    """
    Copy basename of dirname / filename
    """

    await _cn(
        state,
        is_visual=is_visual,
        proc=normpath,
    )


@rpc(blocking=False)
async def _copy_relname(state: State, settings: Settings, is_visual: bool) -> None:
    """
    Copy relname of dirname / filename
    """

    await _cn(
        state,
        is_visual=is_visual,
        proc=lambda p: normpath(p.relative_to(state.root.path)),
    )
