from __future__ import annotations

from dataclasses import dataclass
from enum import Flag, IntEnum
from itertools import chain
from locale import strxfrm
from typing import Any, Callable, Iterable, Iterator, List, Union, cast

from fs import Dir, File, Node


class CompVals(IntEnum):
    FOLDER = 1
    FILE = 2


class Highlights(Flag):
    FILE = 0
    FOLDER = 1
    LINK = 2


@dataclass
class DisplayNode:
    original: Node
    name: str
    children: Iterable[DisplayNode]


def comp(node: Node) -> Iterable[Union[int, str]]:
    if type(node) == File:
        node = cast(File, node)
        return (CompVals.FILE, strxfrm(node.name), strxfrm(node.ext))
    else:
        return (CompVals.FOLDER, strxfrm(node.name))


def dparse(node: Node) -> DisplayNode:
    if type(node) == File:
        return DisplayNode(original=node, name=node.name, children=())
    else:
        node = cast(Dir, node)
        descendants: List[Node] = sorted(
            chain(node.files or (), node.children or ()), key=comp
        )
        children = tuple(map(dparse, descendants))
        return DisplayNode(original=node, name=node.name, children=children)
