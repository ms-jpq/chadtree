from os import getcwd
from typing import Optional

from .cartographer import new
from .render import render
from .types import GitStatus, Settings, State, Node


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


def index(state: State, row: int) -> Optional[Node]:
    if (1 < row) and (row < len(state.lookup)):
        return state.lookup[row]
    else:
        return None
