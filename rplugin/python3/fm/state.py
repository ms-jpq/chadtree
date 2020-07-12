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
    lookup, rendered = render(node, settings=settings, git=git)

    state = State(
        index={cwd},
        selection=set(),
        show_hidden=settings.show_hidden,
        root=node,
        lookup=lookup,
        rendered=rendered,
        git=git,
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
    git: Optional[GitStatus] = None,
) -> State:
    new_root = or_else(root, state.root)
    new_git = or_else(git, state.git)
    lookup, rendered = render(new_root, settings=settings, git=new_git)

    new_state = State(
        index=or_else(index, state.index),
        selection=or_else(selection, state.selection),
        show_hidden=or_else(show_hidden, state.show_hidden),
        root=new_root,
        lookup=lookup,
        rendered=rendered,
        git=new_git,
    )

    return new_state


def index(state: State, row: int) -> Optional[Node]:
    if (row > 0) and (row < len(state.lookup)):
        return state.lookup[row]
    else:
        return None


def is_dir(node: Node) -> bool:
    return Mode.FOLDER in node.mode
