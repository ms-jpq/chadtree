from os import getcwd

from .cartographer import new
from .consts import ignore_json
from .da import load_json
from .types import GitStatus, State


def initial() -> State:
    cwd = getcwd()
    node = new(cwd, index={cwd})

    state = State(
        index=set(),
        selection=set(),
        root=node,
        git=GitStatus(),
        ignore_filter=load_json(ignore_json),
        rendered=(),
        path_lookup=(),
    )
    return state
