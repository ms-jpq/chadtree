from shutil import which
from subprocess import DEVNULL, PIPE, run

from pynvim import Nvim
from pynvim_pp.lib import write

from ..registry import rpc
from ..settings.localization import LANG
from ..settings.types import Settings
from ..state.types import State
from .shared.index import indices
from .types import SysError


def _open_gui(path: str) -> None:
    if which("open"):
        ret = run(("open", path), stdin=DEVNULL, stdout=DEVNULL, stderr=PIPE)
        if ret.returncode != 0:
            raise SysError(ret.stderr)
    elif which("xdg-open"):
        ret = run(("xdg-open", path), stdin=DEVNULL, stdout=DEVNULL, stderr=PIPE)
        if ret.returncode != 0:
            raise SysError(ret.stderr)
    else:
        raise SysError(LANG("sys_open_err"))


@rpc(blocking=False)
def _open_sys(nvim: Nvim, state: State, settings: Settings, is_visual: bool) -> None:
    """
    Open using finder / dolphin, etc
    """

    node = next(indices(nvim, state=state, is_visual=is_visual), None)
    if node:
        try:
            _open_gui(node.path)
        except SysError as e:
            write(nvim, e)
