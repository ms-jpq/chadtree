from os import environ, linesep
from subprocess import DEVNULL, PIPE, run
from typing import AbstractSet, Optional

from pynvim import Nvim
from pynvim_pp.lib import write

from ..registry import rpc
from ..settings.localization import LANG
from ..settings.types import Settings
from ..state.types import State
from .types import Stage


def _sys_search(args: str, cwd: str, sep: str) -> AbstractSet[str]:
    shell = environ["SHELL"]
    cmd = (shell, "-c", args)
    proc = run(cmd, stdin=DEVNULL, stdout=PIPE, stderr=PIPE, text=True)
    return proc.stderr


@rpc(blocking=False)
def _search(nvim: Nvim, state: State, settings: Settings, is_visual: bool) -> Stage:
    """
    New search params
    """

    cwd = state.root.path
    command: Optional[str] = nvim.funcs.input(LANG("new_search"), "")
    if command:
        results = _sys_search(command or "", cwd=cwd, sep=linesep)
        write(nvim, results)

        return Stage(state)
