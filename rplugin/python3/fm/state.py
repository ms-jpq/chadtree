from os import getcwd

from .cartographer import new
from .types import GitStatus, State


def initial() -> State:
    cwd = getcwd()
    state = State(
        index={},
        selection={},
        root=new(cwd, index={cwd}),
        git=GitStatus(),
        rendered=(),
        path_lookup=(),
    )
    return state
