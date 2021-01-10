from concurrent.futures import ThreadPoolExecutor
from typing import Callable, TypeVar

from pynvim_pp.autocmd import AutoCMD
from pynvim_pp.rpc import RPC

T = TypeVar("T")


def _name_gen(fn: Callable[[Callable[..., T]], str]) -> str:
    return f"CHAD{fn.__qualname__.lstrip('_')}"


pool = ThreadPoolExecutor()
autocmd = AutoCMD()
rpc = RPC(name_gen=_name_gen)
