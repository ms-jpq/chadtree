from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, Flag, auto
from itertools import chain
from locale import strxfrm
from typing import Any, Iterable, Iterator, List, Union, cast

from fs import Dir, File, Node


class CompVals(Enum):
    FOLDER = auto()
    FILE = auto()


class Highlights(Flag):
    FILE = auto()
    FOLDER = auto()
    LINK = auto()


@dataclass
class DisplayNode:
    original: Node
    name: str
    children: Iterable[DisplayNode]
    highlight: Highlights


def comp(node: Node) -> Iterable[Union[CompVals, str]]:
    if type(node) == File:
        node = cast(File, node)
        return (CompVals.FILE, strxfrm(node.name), strxfrm(node.ext))
    else:
        return (CompVals.FOLDER, strxfrm(node.name))


def dparse(node: Node) -> DisplayNode:
    if type(node) == File:
        highlight = Highlights.FILE
        if node.is_link:
            highlight = highlight & Highlights.LINK
        return DisplayNode(
            original=node, name=node.name, children=(), highlight=highlight
        )
    else:
        node = cast(Dir, node)
        descendants: List[Node] = sorted(
            chain(node.files or (), node.children or ()), key=comp
        )
        children = tuple(map(dparse, descendants))
        highlight = Highlights.FOLDER
        if node.is_link:
            highlight = highlight & Highlights.LINK
        return DisplayNode(
            original=node, name=node.name, children=children, highlight=highlight
        )


def render(node: DisplayNode) -> List[str]:
    def render(node: DisplayNode, *, depth: int) -> Iterator[str]:
        spaces = depth * 2 * " "
        rend = node.name
        yield spaces + rend
        for child in node.children:
            yield from render(child, depth=depth + 1)

    return [*render(node, depth=0)]
