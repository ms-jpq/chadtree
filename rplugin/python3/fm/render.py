from __future__ import annotations

from enum import IntEnum, auto
from itertools import chain
from locale import strxfrm
from typing import Iterable, Iterator, List, Optional, Union, cast

from .types import DisplayNode, Mode, Node


class CompVals(IntEnum):
    FOLDER = auto()
    FILE = auto()


def comp(node: Node) -> Iterable[Union[int, str]]:
    if Mode.File in node.mode:
        return (CompVals.FOLDER, strxfrm(node.name))
    else:
        node = cast(File, node)
        return (CompVals.FILE, strxfrm(node.name), strxfrm(node.ext))


def dparse(node: Node) -> DisplayNode:
    name = node.name.replace("\n", r"\n")
    if type(node) == File:
        highlight = Highlight.FILE
        if node.is_link:
            highlight = highlight | Highlight.LINK
        return DisplayNode(original=node, name=name, children=(), highlight=highlight)
    else:
        node = cast(Dir, node)
        descendants: List[Node] = sorted(
            chain(node.files or (), node.children or ()), key=comp
        )
        children = tuple(map(dparse, descendants))
        highlight = Highlight.FOLDER
        if node.is_link:
            highlight = highlight | Highlight.LINK
        return DisplayNode(
            original=node, name=name, children=children, highlight=highlight
        )


def decorate(display: str, highlight: Highlight) -> Optional[str]:
    if Highlight.FOLDER in highlight:
        display = display + "/"
    if Highlight.LINK in highlight:
        display = display + " →"
    return display


def render(node: DisplayNode) -> List[str]:
    def render(node: DisplayNode, *, depth: int) -> Iterator[str]:
        spaces = depth * 2 * " "
        rend = node.name
        yield decorate(spaces + rend, node.highlight)
        for child in node.children:
            yield from render(child, depth=depth + 1)

    return [*render(node, depth=0)]
