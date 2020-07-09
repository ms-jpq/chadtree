from __future__ import annotations

from enum import IntEnum, auto
from locale import strxfrm
from typing import Iterable, Iterator, List, Optional, Union

from .types import DisplayNode, Mode, Node


class CompVals(IntEnum):
    FOLDER = auto()
    FILE = auto()


def comp(node: Node) -> Iterable[Union[int, str]]:
    if Mode.FOLDER in node.mode:
        return (CompVals.FOLDER, strxfrm(node.name))
    else:
        return (
            CompVals.FILE,
            strxfrm(node.ext),
            strxfrm(node.name),
        )


def dparse(node: Node, *, depth: int = 0) -> DisplayNode:
    descendants: List[Node] = sorted((node.children or {}).values(), key=comp)
    children = tuple(map(dparse, descendants))
    return DisplayNode(
        path=node.path, mode=node.mode, name=node.name, children=children
    )


def show(node: Node, depth: int) -> Optional[str]:
    if node.hidden:
        return None
    else:
        spaces = depth * 2 * " "
        name = node.name.replace("\n", r"\n")
        if Mode.FOLDER in node.mode:
            name = name + "/"
        if Mode.LINK in node.mode:
            name = name + " →"
        return spaces + name


def render(node: DisplayNode) -> List[str]:
    def render(node: DisplayNode, *, depth: int) -> Iterator[str]:
        rend = show(node, depth)
        if rend:
            yield rend
        for child in node.children:
            yield from render(child, depth=depth + 1)

    return [*render(node, depth=0)]
