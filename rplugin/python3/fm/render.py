from enum import IntEnum, auto
from fnmatch import fnmatch
from locale import strxfrm
from os.path import sep
from typing import Callable, Iterable, Iterator, Optional, Sequence, Tuple, Union

from .da import constantly
from .types import Index, Mode, Node, Selection, Settings, VCStatus


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


def paint(
    settings: Settings, index: Index, selection: Selection
) -> Callable[[Node, int], str]:
    icons = settings.icons

    def show_ascii(node: Node, depth: int) -> str:
        spaces = (depth - 1) * 2 * " "
        select = ""
        name = node.name.replace("\n", r"\n")

        if Mode.FOLDER in node.mode:
            name = f"{name}{sep}"
        if Mode.LINK in node.mode:
            name = f"{name} ->"

        return f"{spaces} {select}{name}"

    def show_icons(node: Node, depth: int) -> str:
        spaces = (depth - 1) * 2 * " "
        select = ""
        name = node.name.replace("\n", r"\n")

        if Mode.FOLDER in node.mode:
            decor = icons.folder_open if node.path in index else icons.folder_closed
            name = f"{decor} {name}"
        else:
            decor = icons.filetype.get(node.ext or "") or next(
                (v for k, v in icons.filename.items() if fnmatch(node.name, k)), None
            )
            if decor:
                name = f"{decor} {name}"
            else:
                name = f"  {name}"
        if Mode.LINK in node.mode:
            name = f"{name} {icons.link}"

        return f"{spaces} {select}{name}"

    show = show_icons if settings.use_icons else show_ascii
    return show


def render(
    node: Node,
    *,
    settings: Settings,
    index: Index,
    selection: Selection,
    vc: VCStatus,
    show_hidden: bool,
) -> Tuple[Sequence[Node], Sequence[str]]:
    drop = constantly(False) if show_hidden else ignore(settings, vc)
    show = paint(settings, index=index, selection=selection)

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
