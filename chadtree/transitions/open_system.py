from asyncio import create_task
from functools import lru_cache
from pathlib import PurePath
from shutil import which as _which
from subprocess import CalledProcessError
from typing import Optional, Sequence, Union

from pynvim_pp.logging import suppress_and_log
from pynvim_pp.nvim import Nvim
from std2 import anext
from std2.asyncio.subprocess import call
from std2.platform import OS, os

from ..registry import rpc
from ..settings.localization import LANG
from ..settings.types import Settings
from ..state.types import State
from .shared.index import indices


@lru_cache(maxsize=None)
def which(path: PurePath) -> Optional[PurePath]:
    if bin := _which(path):
        return PurePath(bin)
    else:
        return None


async def _open_gui(path: PurePath, cwd: PurePath) -> None:
    with suppress_and_log():
        if os is OS.macos and (arg0 := _which("open")):
            argv: Sequence[Union[PurePath, str]] = (arg0, "--", path)
        elif os is OS.linux and (arg0 := _which("xdg-open")):
            argv = (arg0, path)
        elif os is OS.windows and (arg0 := _which("start")):
            argv = (arg0, "", path)
        else:
            await Nvim.write(LANG("sys_open_err"))
            return

        try:
            await call(*argv, cwd=cwd)
        except CalledProcessError as e:
            await Nvim.write(e, e.stderr, e.stdout, error=True)


@rpc(blocking=False)
async def _open_sys(state: State, settings: Settings, is_visual: bool) -> None:
    """
    Open using finder / dolphin, etc
    """

    node = await anext(indices(state, is_visual=is_visual), None)
    if not node:
        return None
    else:
        cwd = await Nvim.getcwd()
        create_task(_open_gui(node.path, cwd=cwd))
