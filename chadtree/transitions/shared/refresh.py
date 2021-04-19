from typing import AbstractSet, Optional

from pynvim import Nvim
from std2.types import Void

from ...fs.ops import ancestors, exists
from ...nvim.quickfix import quickfix
from ...settings.types import Settings
from ...state.next import forward
from ...state.types import State
from ...version_ctl.types import VCStatus
from ..shared.wm import find_current_buffer_name
from ..types import Stage


def refresh(
    nvim: Nvim, state: State, settings: Settings, vc: Optional[VCStatus] = None
) -> Stage:
    current = find_current_buffer_name(nvim)
    cwd = state.root.path
    paths = {cwd}
    new_current = current if cwd in ancestors(current) else None

    index = {path for path in state.index if exists(path, follow=True)} | paths
    selection = {s for s in state.selection if exists(s, follow=False)}
    parent_paths: AbstractSet[str] = ancestors(current) if state.follow else set()
    new_index = index if new_current else index | parent_paths

    qf = quickfix(nvim)
    new_state = forward(
        state,
        settings=settings,
        index=new_index,
        selection=selection,
        qf=qf,
        paths=paths,
        current=new_current or Void,
    )

    return Stage(new_state)
