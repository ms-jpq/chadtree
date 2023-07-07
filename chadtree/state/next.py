from pathlib import PurePath
from typing import AbstractSet, Mapping, Optional, Union, cast

from pynvim_pp.types import ExtData
from std2.types import Void, VoidType, or_else

from ..fs.cartographer import update
from ..fs.types import Node
from ..nvim.types import Markers
from ..settings.types import Settings
from ..version_ctl.types import VCStatus
from ..view.render import render
from .types import FilterPattern, Index, Selection, Session, State


async def forward(
    state: State,
    *,
    settings: Settings,
    root: Union[Node, VoidType] = Void,
    index: Union[Index, VoidType] = Void,
    selection: Union[Selection, VoidType] = Void,
    filter_pattern: Union[Optional[FilterPattern], VoidType] = Void,
    show_hidden: Union[bool, VoidType] = Void,
    follow: Union[bool, VoidType] = Void,
    enable_vc: Union[bool, VoidType] = Void,
    width: Union[int, VoidType] = Void,
    markers: Union[Markers, VoidType] = Void,
    vc: Union[VCStatus, VoidType] = Void,
    current: Union[PurePath, VoidType] = Void,
    invalidate_dirs: Union[AbstractSet[PurePath], VoidType] = Void,
    window_order: Union[Mapping[ExtData, None], VoidType] = Void,
    session: Union[Session, VoidType] = Void,
    trace: bool = True,
) -> State:
    new_index = or_else(index, state.index)
    new_selection = or_else(selection, state.selection)
    new_filter_pattern = or_else(filter_pattern, state.filter_pattern)
    new_current = or_else(current, state.current)
    new_root = cast(
        Node,
        root
        or (
            await update(state.root, index=new_index, invalidate_dirs=invalidate_dirs)
            if not isinstance(invalidate_dirs, VoidType)
            else state.root
        ),
    )
    new_markers = or_else(markers, state.markers)
    new_vc = or_else(vc, state.vc)
    new_hidden = or_else(show_hidden, state.show_hidden)

    derived = render(
        new_root,
        settings=settings,
        index=new_index,
        selection=new_selection,
        filter_pattern=new_filter_pattern,
        markers=new_markers,
        vc=new_vc,
        show_hidden=new_hidden,
        current=new_current,
    )

    new_state = State(
        session=or_else(session, state.session),
        index=new_index,
        selection=new_selection,
        filter_pattern=new_filter_pattern,
        show_hidden=new_hidden,
        follow=or_else(follow, state.follow),
        enable_vc=or_else(enable_vc, state.enable_vc),
        width=or_else(width, state.width),
        root=new_root,
        markers=new_markers,
        vc=new_vc,
        current=new_current,
        derived=derived,
        window_order=or_else(window_order, state.window_order),
    )

    return new_state
