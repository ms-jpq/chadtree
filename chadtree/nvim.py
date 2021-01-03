from typing import Any, Sequence, Tuple, TypeVar

from pynvim import Nvim
from pynvim.api.common import NvimError
from pynvim_pp.lib import async_call

T = TypeVar("T")




async def getcwd(nvim: Nvim) -> str:
    cwd: str = await async_call(nvim, nvim.funcs.getcwd)
    return cwd
