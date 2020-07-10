from __future__ import annotations

from enum import IntEnum, auto
from fnmatch import fnmatch
from locale import strxfrm
from typing import Callable, Iterable, Iterator, Optional, Sequence, Set, Tuple, Union

from .types import GitStatus, Mode, Node, Settings

Ignore = Callable[[Node], bool]


class CompVals(IntEnum):
    FOLDER = auto()
    FILE = auto()


def comp(node: Node) -> Iterable[Union[int, str]]:
    node_type = CompVals.FOLDER if Mode.FOLDER in node.mode else CompVals.FILE
    return (
        node_type,
        strxfrm(node.ext or ""),
        strxfrm(node.name),
    )


def ignore(settings: Settings, git: GitStatus) -> Ignore:
    gitignore = git.ignored

    def drop(node: Node) -> bool:
        path = node.path
        ignore = path in gitignore
        return ignore

    return drop


def show(node: Node, depth: int) -> str:
    spaces = depth * 2 * " "
    name = node.name.replace("\n", r"\n")
    if Mode.FOLDER in node.mode:
        name = name + "/"
    if Mode.LINK in node.mode:
        name = name + " ->"
    return spaces + name


def render(
    node: Node, settings: Settings, git: GitStatus
) -> Tuple[Sequence[str], Sequence[str]]:
    drop = ignore(settings, git)

    def render(node: Node, *, depth: int) -> Iterator[Tuple[str, str]]:
        rend = show(node, depth=depth)
        children = (
            child for child in (node.children or {}).values() if not drop(child)
        )
        yield node.path, rend
        for child in sorted(children, key=comp):
            yield from render(child, depth=depth + 1)

    path_lookup, rendered = zip(*render(node, depth=0))
    return path_lookup, rendered
