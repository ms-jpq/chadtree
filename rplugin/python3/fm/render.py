from enum import IntEnum, auto
from fnmatch import fnmatch
from locale import strxfrm
from os.path import sep
from typing import Callable, Iterable, Iterator, Sequence, Tuple, Union

from .da import constantly
from .types import VCStatus, Mode, Node, Settings


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


def ignore(settings: Settings, vc: VCStatus) -> Callable[[Node], bool]:
    def drop(node: Node) -> bool:
        ignore = (
            node.path in vc.ignored
            or any(fnmatch(node.name, pattern) for pattern in settings.name_ignore)
            or any(fnmatch(node.path, pattern) for pattern in settings.path_ignore)
        )
        return ignore

    return drop


def paint(settings: Settings) -> Callable[[Node, int], str]:
    link_decor = settings.icons.link if settings.use_icons else " ->"

    def show(node: Node, depth: int) -> str:
        spaces = depth * 2 * " "
        name = node.name.replace("\n", r"\n")
        if Mode.FOLDER in node.mode:
            name = name + sep
        if Mode.LINK in node.mode:
            name = name + link_decor
        return spaces + name

    return show


def render(
    node: Node, *, settings: Settings, vc: VCStatus, show_hidden: bool
) -> Tuple[Sequence[Node], Sequence[str]]:
    drop = constantly(False) if show_hidden else ignore(settings, vc)
    show = paint(settings)

    def render(node: Node, *, depth: int) -> Iterator[Tuple[Node, str]]:
        rend = show(node, depth)
        children = (
            child for child in (node.children or {}).values() if not drop(child)
        )
        yield node, rend
        for child in sorted(children, key=comp):
            yield from render(child, depth=depth + 1)

    lookup, rendered = zip(*render(node, depth=0))
    return lookup, rendered
