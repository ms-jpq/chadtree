from os import linesep
from typing import FrozenSet, Optional

from pynvim import Nvim
from pynvim_pp.lib import s_write

from ..registry import rpc
from ..settings.types import Settings
from ..state.types import State
from .types import Stage, SysError


def _search(args: str, cwd: str, sep: str) -> FrozenSet[str]:
    raise SysError()


@rpc(blocking=False, name="CHADsearch")
def c_new_search(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Stage:
    """
    New search params
    """

    cwd = state.root.path
    pattern: Optional[str] = nvim.funcs.input("new_search", "")
    results = _search(pattern or "", cwd=cwd, sep=linesep)
    s_write(nvim, results)

    return Stage(state)
