from pynvim import Nvim
from pynvim_pp.api import list_wins, win_close

from ..registry import rpc
from ..settings.types import Settings
from ..state.types import State
from .shared.wm import find_fm_windows_in_tab


@rpc(blocking=False)
def _quit(nvim: Nvim, state: State, settings: Settings, is_visual: bool) -> None:
    """
    Close sidebar
    """

    wins = list_wins(nvim)
    if len(wins) <= 1:
        nvim.api.command("quit")
    else:
        for win in find_fm_windows_in_tab(nvim, last_used=state.window_order):
            win_close(nvim, win=win)
