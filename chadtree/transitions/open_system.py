from shutil import which
from subprocess import DEVNULL, PIPE, CalledProcessError, check_call

from pynvim import Nvim
from pynvim_pp.lib import write

from ..registry import rpc
from ..settings.localization import LANG
from ..settings.types import Settings
from ..state.types import State
from .shared.index import indices


def _open_gui(path: str) -> None:
    if which("open"):
        command = ("open", "--", path)
        check_call(command, stdin=DEVNULL, stdout=PIPE, stderr=PIPE)
    elif which("xdg-open"):
        command = ("xdg-open", "--", path)
        check_call(command, stdin=DEVNULL, stdout=PIPE, stderr=PIPE)
    else:
        raise LookupError(LANG("sys_open_err"))


@rpc(blocking=False)
def _open_sys(nvim: Nvim, state: State, settings: Settings, is_visual: bool) -> None:
    """
    Open using finder / dolphin, etc
    """

    node = next(indices(nvim, state=state, is_visual=is_visual), None)
    if node:
        try:
            _open_gui(node.path)
        except (CalledProcessError, LookupError) as e:
            write(nvim, e)
