from os.path import exists
from typing import FrozenSet, Optional

from pynvim import Nvim
from pynvim_pp.lib import s_write
from std2.types import Void

from ...fs.ops import ancestors, is_parent
from ...nvim.quickfix import quickfix
from ..shared.wm import find_current_buffer_name, update_buffers
from ...settings.localization import LANG
from ...settings.types import Settings
from ...state.next import forward
from ...state.types import Selection, State
from ...version_ctl.git import status
from ...version_ctl.types import VCStatus
from ..types import Stage


def refresh(
    nvim: Nvim, state: State, settings: Settings, write_out: bool = False
) -> Stage:
    if write_out:
        s_write(nvim, LANG("hourglass"))

    current = find_current_buffer_name(nvim)
    cwd = state.root.path
    paths = frozenset((cwd,))
    new_current = current if is_parent(parent=cwd, child=current) else None

    index = frozenset(i for i in state.index if exists(i)) | paths
    selection: Selection = (
        frozenset()
        if state.filter_pattern
        else frozenset(s for s in state.selection if exists(s))
    )
    current_paths: FrozenSet[str] = ancestors(current) if state.follow else frozenset()
    new_index = index if new_current else index | current_paths

    qf = quickfix(nvim)
    vc = status() if state.enable_vc else VCStatus()
    new_state = forward(
        state,
        settings=settings,
        index=new_index,
        selection=selection,
        qf=qf,
        vc=vc,
        paths=paths,
        current=new_current or Void,
    )

    if write_out:
        s_write(nvim, LANG("ok_sym"))

    return Stage(new_state)




def redraw(nvim: Nvim, state: State, focus: Optional[str]) -> None:
    update_buffers(nvim, state=state, focus=focus)
