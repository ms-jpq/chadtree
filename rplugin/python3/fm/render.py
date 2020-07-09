from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum, auto
from locale import strxfrm
from typing import Callable, Iterable, Iterator, List, Optional, Sequence, Tuple, Union

from .types import Mode, Node


class CompVals(IntEnum):
    FOLDER = auto()
    FILE = auto()


@dataclass(frozen=True)
class DisplayNode:
    path: str
    mode: Mode
    name: str
    children: Iterable[DisplayNode] = field(default_factory=tuple)
    hidden: bool = False


def comp(node: Node) -> Iterable[Union[int, str]]:
    node_type = CompVals.FOLDER if Mode.FOLDER in node.mode else CompVals.FILE
    return (
        node_type,
        strxfrm(node.ext or ""),
        strxfrm(node.name),
    )


def dparse(node: Node, ignore: Callable[[str], bool]) -> DisplayNode:
    descendants: List[Node] = sorted((node.children or {}).values(), key=comp)
    children = tuple(dparse(d, ignore) for d in descendants)
    hidden = ignore(node.path)
    return DisplayNode(
        path=node.path, mode=node.mode, name=node.name, children=children, hidden=hidden
    )


def show(node: DisplayNode, depth: int) -> Optional[str]:
    if node.hidden:
        return None
    else:
        spaces = depth * 2 * " "
        name = node.name.replace("\n", r"\n")
        if Mode.FOLDER in node.mode:
            name = name + "/"
        if Mode.LINK in node.mode:
            name = name + " ->"
        return spaces + name


def render(
    node: Node, ignore: Callable[[str], bool]
) -> Tuple[Sequence[str], Sequence[str]]:
    def render(node: DisplayNode, *, depth: int) -> Iterator[Tuple[str, str]]:
        rend = show(node, depth)
        if rend:
            yield node.path, rend
        for child in node.children:
            yield from render(child, depth=depth + 1)

    dnode = dparse(node, ignore=ignore)
    path_lookup, rendered = zip(*render(dnode, depth=0))
    return path_lookup, rendered
