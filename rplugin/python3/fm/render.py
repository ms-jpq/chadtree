from __future__ import annotations

from dataclasses import dataclass
from enum import Flag, IntEnum, auto
from itertools import chain
from locale import strxfrm
from typing import Iterable, Iterator, List, Optional, Set, Union, cast

from .fs import Dir, File, Node


class CompVals(IntEnum):
    FOLDER = auto()
    FILE = auto()


class Highlight(Flag):
    FILE = auto()
    FOLDER = auto()
    LINK = auto()


@dataclass
class DisplayNode:
    original: Node
    name: str
    children: Iterable[DisplayNode]
    highlight: Highlight


@dataclass
class DisplayIndex:
    index: Set[str]
    root: DisplayNode


def comp(node: Node) -> Iterable[Union[int, str]]:
    if type(node) == Dir:
        return (CompVals.FOLDER, strxfrm(node.name))
    else:
        node = cast(File, node)
        return (CompVals.FILE, strxfrm(node.name), strxfrm(node.ext))


def dparse(node: Node) -> DisplayNode:
    if type(node) == File:
        highlight = Highlight.FILE
        if node.is_link:
            highlight = highlight | Highlight.LINK
        return DisplayNode(
            original=node, name=node.name, children=(), highlight=highlight
        )
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
            original=node, name=node.name, children=children, highlight=highlight
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
