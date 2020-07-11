from os import getcwd
from typing import Optional

from .cartographer import new
from .render import render
from .types import GitStatus, Settings, State


def initial(settings: Settings) -> State:
    cwd = getcwd()
    node = new(cwd, index={cwd})
    path_lookup, rendered = render(node, settings=settings, git=GitStatus())

    state = State(
        index=set(),
        selection=set(),
        show_hidden=settings.show_hidden,
        root=node,
        path_lookup=path_lookup,
        rendered=rendered,
    )
    return state


def index(state: State, row: int) -> Optional[str]:
    if (1 < row) and (row < len(state.path_lookup)):
        return state.path_lookup[row]
    else:
        return None
