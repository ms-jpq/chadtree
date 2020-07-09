from asyncio import get_event_loop, run_coroutine_threadsafe
from concurrent.futures import ThreadPoolExecutor
from typing import Awaitable

from pynvim import Nvim, autocmd, command, plugin


@plugin
class Main:
    def __init__(self, nvim: Nvim):
        self.chan = ThreadPoolExecutor(max_workers=1)
        self.nvim = nvim

    # Work around for coroutine deadlocks
    def _submit(self, coro: Awaitable[None]) -> None:
        loop = get_event_loop()

        def stage() -> None:
            fut = run_coroutine_threadsafe(coro, loop)
            fut.result()

        self.chan.submit(stage)

    @command("FMOPEN")
    def fm_open(self, *args) -> None:
        self.nvim.current.line = "OWO"

    @autocmd("BufEnter", pattern="*")
    def on_bufenter(self) -> None:
        async def commit() -> None:
            self.nvim.out_write("reeeeeeeeeeee" + "\n")

        self._submit(commit())
