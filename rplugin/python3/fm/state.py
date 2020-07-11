from os import getcwd
from typing import Optional, Sequence

from .cartographer import new
from .da import or_else
from .render import render
from .types import GitStatus, Index, Mode, Node, Selection, Settings, State


def initial(settings: Settings) -> State:
    cwd = getcwd()
    node = new(cwd, index={cwd})
    git = GitStatus()
    path_lookup, rendered = render(node, settings=settings, git=git)

    state = State(
        index=set(),
        selection=set(),
        show_hidden=settings.show_hidden,
        root=node,
        lookup=path_lookup,
        rendered=rendered,
        git=git,
    )
    return state


def merge(
    state: State,
    *,
    index: Optional[Index] = None,
    selection: Optional[Selection] = None,
    show_hidden: Optional[bool] = None,
    root: Optional[Node] = None,
    lookup: Optional[Sequence[Node]] = None,
    rendered: Optional[Sequence[str]] = None,
    git: Optional[GitStatus] = None,
) -> State:
    new_state = State(
        index=or_else(index, state.index),
        selection=or_else(selection, state.selection),
        show_hidden=or_else(show_hidden, state.show_hidden),
        root=or_else(root, state.root),
        lookup=or_else(lookup, state.lookup),
        rendered=or_else(rendered, state.rendered),
        git=or_else(git, state.git),
    )

    return new_state


def index(state: State, row: int) -> Optional[Node]:
    if (row > 0) and (row < len(state.lookup)):
        return state.lookup[row]
    else:
        return None


def is_dir(node: Node) -> bool:
    return Mode.FOLDER in node.mode
