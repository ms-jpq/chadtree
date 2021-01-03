from typing import Any, Sequence, Tuple, TypeVar

from pynvim import Nvim
from pynvim.api.common import NvimError
from pynvim_pp.lib import async_call

T = TypeVar("T")


def atomic(nvim: Nvim, *instructions: Tuple[str, Sequence[Any]]) -> Sequence[Any]:
    inst = tuple((f"nvim_{instruction}", args) for instruction, args in instructions)
    out, err = nvim.api.call_atomic(inst)
    if err:
        raise NvimError(err)
    return out


async def getcwd(nvim: Nvim) -> str:
    cwd: str = await async_call(nvim, nvim.funcs.getcwd)
    return cwd
