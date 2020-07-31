from enum import IntEnum, auto
from fnmatch import fnmatch
from locale import strxfrm
from os import linesep
from os.path import sep
from typing import Callable, Iterator, Optional, Sequence, Tuple, cast

from .da import constantly
from .types import (
    Badge,
    Highlight,
    HLgroup,
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


def ignore(settings: Settings, vc: VCStatus, filtering: str) -> Callable[[Node], bool]:
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
    context = settings.hl_context
    icon_lookup = settings.icons.ext_colours
    mode_lookup_pre, mode_lookup_post, ext_lookup, name_lookup = (
        context.mode_lookup_pre,
        context.mode_lookup_post,
        context.ext_lookup,
        context.name_lookup,
    )
    icons = settings.icons
    use_icons = settings.use_icons

    def search_hl(node: Node) -> Optional[HLgroup]:
        s_modes = sorted(node.mode)

        for mode in s_modes:
            hl = mode_lookup_pre.get(mode)
            if hl:
                return hl
        hl = ext_lookup.get(node.ext or "")
        if hl:
            return hl
        for pattern, group in name_lookup.items():
            if fnmatch(node.name, pattern):
                return group
        for mode in s_modes:
            hl = mode_lookup_post.get(mode)
            if hl:
                return hl

        return mode_lookup_post.get(None)

    def gen_spacer(depth: int) -> str:
        return (depth * 2 - 1) * " "

    def gen_status(path: str) -> str:
        selected = icons.selected if path in selection else " "
        active = icons.active if path == current else " "
        return f"{selected}{active}"

    def gen_decor_pre(node: Node, depth: int) -> Iterator[str]:
        yield gen_spacer(depth)
        yield gen_status(node.path)

    def gen_icon(node: Node) -> Iterator[str]:
        yield " "
        if Mode.folder in node.mode:
            yield icons.folder_open if node.path in index else icons.folder_closed
        else:
            yield (
                icons.filename_exact.get(node.name, "")
                or icons.filetype.get(node.ext or "", "")
                or next(
                    (
                        v
                        for k, v in icons.filename_glob.items()
                        if fnmatch(node.name, k)
                    ),
                    icons.default_icon,
                )
            ) if use_icons else icons.default_icon
        yield " "

    def gen_name(node: Node) -> Iterator[str]:
        yield node.name.replace(linesep, r"\n")
        if not use_icons and Mode.folder in node.mode:
            yield sep

    def gen_decor_post(node: Node) -> Iterator[str]:
        mode = node.mode
        if Mode.orphan_link in mode:
            yield " "
            yield icons.link_broken
        elif Mode.link in mode:
            yield " "
            yield icons.link

    def gen_badges(path: str) -> Iterator[Badge]:
        qf_count = qf.locations[path]
        stat = vc.status.get(path)
        if qf_count:
            yield Badge(text=f"({qf_count})", group=icons.quickfix_hl)
        if stat:
            yield Badge(text=f"[{stat}]", group=icons.version_ctl_hl)

    def gen_highlights(
        node: Node, pre: str, icon: str, name: str
    ) -> Iterator[Highlight]:
        begin = len(pre.encode())
        end = begin + len(icon.encode())
        group = icon_lookup.get(node.ext or "")
        if group:
            hl = Highlight(group=group.name, begin=begin, end=end)
            yield hl
        group = search_hl(node)
        if group:
            begin = end
            end = len(name.encode()) + begin
            hl = Highlight(group=group.name, begin=begin, end=end)
            yield hl

    def show(node: Node, depth: int) -> Render:
        pre = "".join(gen_decor_pre(node, depth=depth))
        icon = "".join(gen_icon(node))
        name = "".join(gen_name(node))
        post = "".join(gen_decor_post(node))

        line = f"{pre}{icon}{name}{post}"
        badges = tuple(gen_badges(node.path))
        highlights = tuple(gen_highlights(node, pre=pre, icon=icon, name=name))
        render = Render(line=line, badges=badges, highlights=highlights)
        return render

    return show


def render(
    node: Node,
    *,
    settings: Settings,
    index: Index,
    selection: Selection,
    filtering: str,
    qf: QuickFix,
    vc: VCStatus,
    show_hidden: bool,
    current: Optional[str],
) -> Tuple[Sequence[Node], Sequence[Render]]:
    drop = (
        constantly(False)
        if show_hidden
        else ignore(settings, vc=vc, filtering=filtering)
    )
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
