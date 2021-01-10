from typing import Sequence

from pynvim import Nvim
from pynvim.api import Window

from ..registry import rpc
from ..settings.types import Settings
from ..state.types import State
from .shared.wm import find_fm_windows_in_tab


def _kill_fm_windows(nvim: Nvim) -> None:
    windows: Sequence[Window] = nvim.api.list_wins()
    if len(windows) <= 1:
        nvim.api.command("quit")
    else:
        for window in find_fm_windows_in_tab(nvim):
            nvim.api.win_close(window, True)


@rpc(blocking=False)
def _quit(nvim: Nvim, state: State, settings: Settings, is_visual: bool) -> None:
    """
    Close sidebar
    """

    _kill_fm_windows(nvim)
