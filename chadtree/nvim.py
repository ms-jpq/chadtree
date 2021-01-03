from pynvim import Nvim
from pynvim_pp.lib import async_call


async def getcwd(nvim: Nvim) -> str:
    cwd: str = await async_call(nvim, nvim.funcs.getcwd)
    return cwd
