from pynvim_pp.nvim import Nvim
from pynvim_pp.window import Window

from ..registry import rpc
from ..state.types import State
from .shared.wm import find_fm_windows_in_tab


@rpc(blocking=False)
async def _quit(state: State, is_visual: bool) -> None:
    """
    Close sidebar
    """

    wins = await Window.list()
    if len(wins) <= 1:
        await Nvim.exec("quit")
    else:
        async for win in find_fm_windows_in_tab(state.window_order):
            await win.close()
