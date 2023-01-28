import sys
from asyncio import create_task
from pathlib import PurePath
from subprocess import CalledProcessError

from pynvim_pp.logging import suppress_and_log
from pynvim_pp.nvim import Nvim
from std2 import anext
from std2.asyncio.subprocess import call
from std2.pathlib import AnyPath
from std2.platform import OS, os

from ..fs.ops import which
from ..registry import rpc
from ..settings.localization import LANG
from ..settings.types import Settings
from ..state.types import State
from .shared.index import indices


async def _call(cwd: PurePath, arg0: AnyPath, *args: AnyPath) -> None:
    try:
        await call(arg0, *args, cwd=cwd)
    except CalledProcessError as e:
        await Nvim.write(e, e.stderr, e.stdout, error=True)


async def _open_gui(path: PurePath, cwd: PurePath) -> None:
    with suppress_and_log():
        if sys.platform == "win32":
            from os import startfile

            startfile(path, cwd=cwd)
        elif os is OS.macos and (arg0 := which("open")):
            await _call(cwd, arg0, "--", path)
        elif os is OS.linux and (arg0 := which("xdg-open")):
            await _call(cwd, arg0, path)
        else:
            await Nvim.write(LANG("sys_open_err"))


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
