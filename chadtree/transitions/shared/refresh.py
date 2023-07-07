from asyncio import gather
from pathlib import PurePath
from typing import AbstractSet, Mapping

from pynvim_pp.types import ExtData
from pynvim_pp.window import Window
from std2.types import Void

from ...fs.ops import ancestors, exists_many
from ...nvim.markers import markers
from ...settings.types import Settings
from ...state.next import forward
from ...state.types import State
from ..shared.wm import find_current_buffer_path
from ..types import Stage


async def _index(state: State, paths: AbstractSet[PurePath]) -> AbstractSet[PurePath]:
    index = {
        path
        for path, exists in (await exists_many(state.index, follow=True)).items()
        if exists
    } | paths

    return index


async def _selection(state: State) -> AbstractSet[PurePath]:
    selection = {
        selected
        for selected, exists in (
            await exists_many(state.selection, follow=False)
        ).items()
        if exists
    }

    return selection


async def _window_order(state: State) -> Mapping[ExtData, None]:
    window_ids = {w.data for w in await Window.list()}
    window_order = {
        win_id: None for win_id in state.window_order if win_id in window_ids
    }
    return window_order


async def refresh(state: State, settings: Settings) -> Stage:
    cwd = state.root.path
    paths = {cwd}

    current, index, selection, window_order, mks = await gather(
        find_current_buffer_path(),
        _index(state, paths=paths),
        _selection(state),
        _window_order(state),
        markers(),
    )
    current_ancestors = ancestors(current) if current else frozenset()
    new_current = current if cwd in current_ancestors else None

    parent_paths: AbstractSet[PurePath] = (
        current_ancestors if state.follow else frozenset()
    )
    new_index = index if new_current else index | parent_paths

    new_state = await forward(
        state,
        settings=settings,
        index=new_index,
        selection=selection,
        markers=mks,
        paths=paths,
        current=new_current or Void,
        window_order=window_order,
        trace=False,
    )

    return Stage(new_state)
