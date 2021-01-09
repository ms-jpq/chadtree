from locale import strxfrm
from operator import add, sub
from os import linesep
from os.path import dirname, join, relpath
from typing import (
    Callable,
    FrozenSet,
    Iterator,
    Mapping,
    Optional,
    Sequence,
)

from pynvim import Nvim
from pynvim.api.window import Window
from pynvim_pp.lib import s_write

from .fs.cartographer import new as new_root
from .fs.ops import (
    ancestors,
    is_parent,
    new,
    rename,
)
from .fs.types import Mode
from .nvim.quickfix import quickfix
from .nvim.wm import (
    find_current_buffer_name,
    kill_buffers,
    kill_fm_windows,
    resize_fm_windows,
    toggle_fm_window,
    update_buffers,
)
from .registry import autocmd, rpc
from .settings.localization import LANG
from .settings.types import Settings
from .state.ops import dump_session
from .state.next import forward
from .fs.cartographer import is_dir
from .state.types import FilterPattern, Selection, State, VCStatus


def redraw(nvim: Nvim, state: State, focus: Optional[str]) -> None:
    update_buffers(nvim, state=state, focus=focus)


def _current(
    nvim: Nvim, state: State, settings: Settings, current: str
) -> Optional[Stage]:
    if is_parent(parent=state.root.path, child=current):
        paths: FrozenSet[str] = (
            frozenset(ancestors(current)) if state.follow else frozenset()
        )
        index = state.index | paths
        new_state = forward(
            state, settings=settings, index=index, paths=paths, current=current
        )
        return Stage(new_state)
    else:
        return None




