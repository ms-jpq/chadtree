from os import getcwd

from .cartographer import new
from .types import GitStatus, State


def initial() -> State:
    cwd = getcwd()
    node = new(cwd, index={cwd})

    state = State(
        index=set(),
        selection=set(),
        root=node,
        git=GitStatus(),
        rendered=(),
        path_lookup=(),
    )
    return state
