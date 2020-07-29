from enum import IntEnum, auto
from fnmatch import fnmatch
from locale import strxfrm
from os import linesep
from os.path import sep
from typing import Callable, Iterator, Optional, Sequence, Tuple, cast

from .da import constantly
from .types import (
    Badge,
    Index,
    Mode,
    Node,
    QuickFix,
    Render,
    Selection,
    Settings,
    VCStatus,
)


class CompVals(IntEnum):
    FOLDER = auto()
    FILE = auto()


def comp(node: Node) -> Tuple[int, str, str]:
    node_type = CompVals.FOLDER if Mode.folder in node.mode else CompVals.FILE
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
    settings: Settings,
    index: Index,
    selection: Selection,
    qf: QuickFix,
    vc: VCStatus,
    current: Optional[str],
) -> Callable[[Node, int], Render]:
    icons = settings.icons
    use_icons = settings.use_icons

    sym_active = icons.active if use_icons else ">"
    sym_select = icons.selected if use_icons else "*"
    sym_link = icons.link if use_icons else "->"
    sym_link_broken = icons.link_broken if use_icons else "-/->"
    sym_folder_open = icons.folder_open if use_icons else "-"
    sym_folder_closed = icons.folder_closed if use_icons else "+"

    def gen_spacer(depth: int) -> str:
        return (depth * 2 - 1) * " "

    def gen_status(path: str) -> str:
        selected = sym_select if path in selection else " "
        active = sym_active if path == current else " "
        return f"{selected}{active}"

    def gen_badges(path: str) -> Iterator[Badge]:
        qf_count = qf.locations[path]
        stat = vc.status.get(path)
        if qf_count:
            yield Badge(text=f"({qf_count})", group="Label")
        if stat:
            yield Badge(text=f"[{stat}]", group="Comment")

    def gen_decor_pre(node: Node, depth: int) -> Iterator[str]:
        yield gen_spacer(depth)
        yield gen_status(node.path)
        yield " "
        if Mode.folder in node.mode:
            yield sym_folder_open if node.path in index else sym_folder_closed
        else:
            yield (
                icons.filetype.get(node.ext or "", "")
                or next(
                    (v for k, v in icons.filename.items() if fnmatch(node.name, k)),
                    " ",
                )
            ) if use_icons else " "
        yield " "

    def gen_name(node: Node) -> Iterator[str]:
        yield node.name.replace(linesep, r"\n")
        if not use_icons and Mode.folder in node.mode:
            yield sep

    def gen_decor_post(node: Node) -> Iterator[str]:
        mode = node.mode
        yield " "
        if Mode.orphan_link in mode:
            yield sym_link_broken
        elif Mode.link in mode:
            yield sym_link

    def show(node: Node, depth: int) -> Render:
        pre = "".join(gen_decor_pre(node, depth=depth))
        name = "".join(gen_name(node))
        post = "".join(gen_decor_post(node))

        line = f"{pre}{name}{post}"
        badges = tuple(gen_badges(node.path))
        render = Render(line=line, badges=badges, highlights=())
        return render

    return show


def render(
    node: Node,
    *,
    settings: Settings,
    index: Index,
    selection: Selection,
    qf: QuickFix,
    vc: VCStatus,
    show_hidden: bool,
    current: Optional[str],
) -> Tuple[Sequence[Node], Sequence[Render]]:
    drop = constantly(False) if show_hidden else ignore(settings, vc)
    show = paint(
        settings, index=index, selection=selection, qf=qf, vc=vc, current=current
    )

    def render(node: Node, *, depth: int) -> Iterator[Tuple[Node, Render]]:
        rend = show(node, depth)
        children = (
            child for child in (node.children or {}).values() if not drop(child)
        )
        yield node, rend
        for child in sorted(children, key=comp):
            yield from render(child, depth=depth + 1)

    lookup, rendered = zip(*render(node, depth=0))
    return cast(Sequence[Node], lookup), cast(Sequence[Render], rendered)
