from pathlib import PurePath
from typing import AbstractSet, Mapping, Optional, Union, cast

from pynvim_pp.rpc_types import ExtData
from std2.types import Void, VoidType, or_else

from ..fs.cartographer import update
from ..fs.types import Node
from ..nvim.types import Markers
from ..version_ctl.types import VCStatus
from .cache import DeepState
from .types import Diagnostics, FilterPattern, Index, Selection, Session, State


async def forward(
    state: State,
    *,
    root: Union[Node, VoidType] = Void,
    index: Union[Index, VoidType] = Void,
    selection: Union[Selection, VoidType] = Void,
    filter_pattern: Union[Optional[FilterPattern], VoidType] = Void,
    show_hidden: Union[bool, VoidType] = Void,
    follow: Union[bool, VoidType] = Void,
    follow_links: Union[bool, VoidType] = Void,
    follow_ignore: Union[bool, VoidType] = Void,
    enable_vc: Union[bool, VoidType] = Void,
    width: Union[int, VoidType] = Void,
    markers: Union[Markers, VoidType] = Void,
    diagnostics: Union[Diagnostics, VoidType] = Void,
    vc: Union[VCStatus, VoidType] = Void,
    current: Union[PurePath, VoidType] = Void,
    invalidate_dirs: Union[AbstractSet[PurePath], VoidType] = Void,
    window_order: Union[Mapping[ExtData, None], VoidType] = Void,
    session: Union[Session, VoidType] = Void,
    vim_focus: Union[bool, VoidType] = Void,
    trace: bool = True,
) -> State:
    new_index = or_else(index, state.index)
    new_selection = or_else(selection, state.selection)
    new_filter_pattern = or_else(filter_pattern, state.filter_pattern)
    new_current = or_else(current, state.current)
    new_follow_links = or_else(follow_links, state.follow_links)
    new_root = cast(
        Node,
        root
        or (
            await update(
                state.executor,
                root=state.root,
                follow_links=new_follow_links,
                index=new_index,
                invalidate_dirs=invalidate_dirs,
            )
            if not isinstance(invalidate_dirs, VoidType)
            else state.root
        ),
    )
    new_markers = or_else(markers, state.markers)
    new_vc = or_else(vc, state.vc)
    new_hidden = or_else(show_hidden, state.show_hidden)
    new_vim_focus = or_else(vim_focus, state.vim_focus)

    new_state = DeepState(
        executor=state.executor,
        settings=state.settings,
        session=or_else(session, state.session),
        vim_focus=new_vim_focus,
        index=new_index,
        selection=new_selection,
        filter_pattern=new_filter_pattern,
        show_hidden=new_hidden,
        follow=or_else(follow, state.follow),
        follow_links=new_follow_links,
        follow_ignore=or_else(follow_ignore, state.follow_ignore),
        enable_vc=or_else(enable_vc, state.enable_vc),
        width=or_else(width, state.width),
        root=new_root,
        markers=new_markers,
        diagnostics=or_else(diagnostics, state.diagnostics),
        vc=new_vc,
        current=new_current,
        window_order=or_else(window_order, state.window_order),
    )

    return new_state
