from pathlib import PurePath
from threading import Lock

from pynvim import Nvim
from pynvim_pp.api import get_cwd
from pynvim_pp.logging import log

from ..registry import enqueue_event, pool, rpc
from ..settings.types import Settings
from ..state.next import forward
from ..state.types import State
from ..version_ctl.git import status
from ..version_ctl.types import VCStatus
from .types import Stage

_lock = Lock()


@rpc(blocking=False)
def _set_vc(nvim: Nvim, state: State, settings: Settings, vc: VCStatus) -> Stage:
    new_state = forward(state, settings=settings, vc=vc)
    return Stage(new_state)


@rpc(blocking=False)
def vc_refresh(nvim: Nvim, state: State, settings: Settings) -> None:
    """
    VC Refresh
    """

    if state.enable_vc:
        cwd = PurePath(get_cwd(nvim))

        def cont() -> None:
            if _lock.locked():
                pass
            else:
                with _lock:
                    try:
                        vc = status(cwd)
                    except Exception as e:
                        log.exception("%s", e)
                    else:
                        enqueue_event(_set_vc, vc)

        pool.submit(cont)

