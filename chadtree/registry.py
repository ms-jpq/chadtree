from concurrent.futures import ThreadPoolExecutor
from queue import SimpleQueue
from typing import Any, Callable, TypeVar

from pynvim_pp.autocmd import AutoCMD
from pynvim_pp.logging import log
from pynvim_pp.rpc import RPC, RpcCallable, RpcMsg

T = TypeVar("T")


def _name_gen(fn: Callable[[Callable[..., T]], str]) -> str:
    return f"CHAD{fn.__qualname__.lstrip('_')}"


pool = ThreadPoolExecutor()
event_queue: SimpleQueue = SimpleQueue()
autocmd = AutoCMD()
rpc = RPC(name_gen=_name_gen)


def enqueue_event(event: RpcCallable, *args: Any) -> None:
    try:
        msg: RpcMsg = (event.name, args)
        event_queue.put(msg)
    except Exception as e:
        log.exception("%s", e)
        raise
