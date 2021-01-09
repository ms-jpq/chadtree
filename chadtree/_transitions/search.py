from asyncio.subprocess import DEVNULL, PIPE
from typing import Set


from .types import SysError

def _search(args: str, cwd: str, sep: str) -> Set[str]:
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
    results = search(pattern or "", cwd=cwd, sep=linesep)
    s_write(nvim, results)

    return Stage(state)
