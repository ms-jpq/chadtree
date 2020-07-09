from asyncio import get_event_loop, run_coroutine_threadsafe
from typing import Awaitable

from pynvim import Nvim, autocmd, command, plugin

from .consts import threadpool


# Work around for coroutine deadlocks
def _submit(coro: Awaitable[None]) -> None:
    loop = get_event_loop()

    def stage() -> None:
        fut = run_coroutine_threadsafe(coro, loop)
        fut.result()

    threadpool.submit(stage)


@plugin
class Main:
    def __init__(self, nvim: Nvim):
        self.nvim = nvim

    @command("FMOPEN")
    def fm_open(self, *args) -> None:
        self.nvim.current.line = "OWO"

    @autocmd("BufEnter", pattern="*")
    def on_bufenter(self) -> None:
        async def commit() -> None:
            self.nvim.out_write("reeeeeeeeeeee" + "\n")

        _submit(commit())
