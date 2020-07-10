from os import getcwd

from .cartographer import new
from .render import render
from .types import GitStatus, Settings, State


def initial(settings: Settings) -> State:
    cwd = getcwd()
    node = new(cwd, index={cwd})
    path_lookup, rendered = render(node, settings=settings, git=GitStatus())

    state = State(index=set(), selection=set(), root=node, rendered=(), path_lookup=())
    return state
