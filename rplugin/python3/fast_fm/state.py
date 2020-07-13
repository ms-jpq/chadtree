from os import getcwd
from typing import Optional, Sequence

from .cartographer import new, update
from .da import or_else
from .render import render
from .types import Index, Mode, Node, Selection, Set, Settings, State, VCStatus


def initial(settings: Settings) -> State:
    cwd = getcwd()
    index = {cwd}
    selection: Selection = set()
    node = new(cwd, index=index)
    vc = VCStatus()
    lookup, rendered = render(
        node,
        settings=settings,
        index=index,
        selection=selection,
        vc=vc,
        show_hidden=settings.show_hidden,
    )

    state = State(
        index=index,
        selection=selection,
        show_hidden=settings.show_hidden,
        follow=settings.follow,
        root=node,
        lookup=lookup,
        rendered=rendered,
        vc=vc,
    )
    return state


async def forward(
    state: State,
    *,
    settings: Settings,
    index: Optional[Index] = None,
    selection: Optional[Selection] = None,
    show_hidden: Optional[bool] = None,
    follow: Optional[bool] = None,
    root: Optional[Node] = None,
    lookup: Optional[Sequence[Node]] = None,
    rendered: Optional[Sequence[str]] = None,
    vc: Optional[VCStatus] = None,
    paths: Optional[Set[str]] = None,
) -> State:
    new_index = or_else(index, state.index)
    new_selection = or_else(selection, state.selection)
    new_root = (
        await update(state.root, index=new_index, paths=paths) if paths else state.root
    )
    new_vc = or_else(vc, state.vc)
    new_hidden = or_else(show_hidden, state.show_hidden)
    lookup, rendered = render(
        new_root,
        settings=settings,
        index=new_index,
        selection=new_selection,
        vc=new_vc,
        show_hidden=new_hidden,
    )

    new_state = State(
        index=new_index,
        selection=new_selection,
        show_hidden=new_hidden,
        follow=or_else(follow, state.follow),
        root=new_root,
        lookup=lookup,
        rendered=rendered,
        vc=new_vc,
    )

    return new_state


def index(state: State, row: int) -> Optional[Node]:
    if (row > 0) and (row < len(state.lookup)):
        return state.lookup[row]
    else:
        return None


def is_dir(node: Node) -> bool:
    return Mode.FOLDER in node.mode
