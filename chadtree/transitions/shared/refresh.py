from os.path import exists
from typing import AbstractSet

from pynvim import Nvim
from pynvim_pp.lib import write
from std2.types import Void

from ...fs.ops import ancestors
from ...nvim.quickfix import quickfix
from ...settings.localization import LANG
from ...settings.types import Settings
from ...state.next import forward
from ...state.types import Selection, State
from ..shared.wm import find_current_buffer_name
from ..types import Stage


def refresh(
    nvim: Nvim, state: State, settings: Settings, write_out: bool = False
) -> Stage:
    if write_out:
        write(nvim, LANG("hourglass"))

    current = find_current_buffer_name(nvim)
    cwd = state.root.path
    paths = {cwd}
    new_current = current if cwd in ancestors(current) else None

    index = {path for path in state.index if exists(path)} | paths
    selection: Selection = (
        set() if state.filter_pattern else {s for s in state.selection if exists(s)}
    )
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

    if write_out:
        write(nvim, LANG("ok_sym"))

    return Stage(new_state)
