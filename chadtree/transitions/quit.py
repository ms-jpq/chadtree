from pynvim import Nvim

from ..registry import rpc
from ..settings.types import Settings
from ..state.types import State
from .shared.wm import kill_fm_windows


@rpc(blocking=False)
def _quit(nvim: Nvim, state: State, settings: Settings, is_visual: bool) -> None:
    """
    Close sidebar
    """

    kill_fm_windows(nvim)
