from webbrowser import open as open_w

from pynvim import Nvim
from pynvim_pp.api import create_buf
from pynvim_pp.float_win import open_float_win, list_floatwins

from ..registry import rpc
from ..settings.types import Settings
from ..state.types import State


@rpc(blocking=False)
def _help(nvim: Nvim, state: State, settings: Settings, is_visual: bool) -> None:
    """
    Open help doc
    """

    buf = create_buf(nvim, listed=False, scratch=True, wipe=True, nofile=True)
    open_float_win(nvim, margin=0, relsize=0.95, buf=buf)