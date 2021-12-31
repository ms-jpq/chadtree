from pathlib import PurePath
from typing import AbstractSet

from pynvim import Nvim
from std2.types import Void

from ...fs.ops import ancestors, exists
from ...nvim.markers import markers
from ...settings.types import Settings
from ...state.types import State
from ...state.next import forward
from ..shared.wm import find_current_buffer_name
from ..types import Stage


def refresh(nvim: Nvim, state: State, settings: Settings) -> Stage:
    current = find_current_buffer_name(nvim)
    cwd = state.root.path
    paths = {cwd}
    new_current = current if cwd in ancestors(current) else None

    index = {path for path in state.index if exists(path, follow=True)} | paths
    selection = {s for s in state.selection if exists(s, follow=False)}
    parent_paths: AbstractSet[PurePath] = ancestors(current) if state.follow else set()
    new_index = index if new_current else index | parent_paths

    mks = markers(nvim)
    new_state = forward(
        state,
        settings=settings,
        index=new_index,
        selection=selection,
        markers=mks,
        paths=paths,
        current=new_current or Void,
    )

    return Stage(new_state)
