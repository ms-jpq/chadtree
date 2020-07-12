from os import getcwd
from typing import Optional, Sequence

from .cartographer import new
from .da import or_else
from .render import render
from .types import Index, Mode, Node, Selection, Settings, State, VCStatus


def initial(settings: Settings) -> State:
    cwd = getcwd()
    index = {cwd}
    node = new(cwd, index=index)
    vc = VCStatus()
    lookup, rendered = render(
        node, settings=settings, vc=vc, show_hidden=settings.show_hidden
    )

    state = State(
        index=index,
        selection=set(),
        show_hidden=settings.show_hidden,
        root=node,
        lookup=lookup,
        rendered=rendered,
        vc=vc,
    )
    return state


def forward(
    state: State,
    *,
    settings: Settings,
    index: Optional[Index] = None,
    selection: Optional[Selection] = None,
    show_hidden: Optional[bool] = None,
    root: Optional[Node] = None,
    lookup: Optional[Sequence[Node]] = None,
    rendered: Optional[Sequence[str]] = None,
    vc: Optional[VCStatus] = None,
) -> State:
    new_root = or_else(root, state.root)
    new_vc = or_else(vc, state.vc)
    new_hidden = or_else(show_hidden, state.show_hidden)
    lookup, rendered = render(
        new_root, settings=settings, vc=new_vc, show_hidden=new_hidden,
    )

    new_state = State(
        index=or_else(index, state.index),
        selection=or_else(selection, state.selection),
        show_hidden=new_hidden,
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
