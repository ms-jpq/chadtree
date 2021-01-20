from enum import IntEnum, auto
from fnmatch import fnmatch
from locale import strxfrm
from os import linesep
from os.path import sep
from typing import Any, Callable, Iterator, Optional, Sequence, Tuple, cast

from pynvim_pp.highlight import highlight
from std2.types import never

from ..fs.cartographer import is_dir
from ..fs.types import Mode, Node
from ..settings.types import IgnoreOpts, Settings
from ..state.types import FilterPattern, Index, QuickFix, Selection
from ..version_ctl.types import VCStatus
from .types import Badge, Derived, Highlight, Sortby


class _CompVals(IntEnum):
    FOLDER = auto()
    FILE = auto()


Render = Tuple[str, Sequence[Highlight], Sequence[Badge]]
NRender = Tuple[Node, str, Sequence[Highlight], Sequence[Badge]]


def _gen_comp(sortby: Sequence[Sortby]) -> Callable[[Node], Any]:
    def comp(node: Node) -> Sequence[Any]:
        def cont() -> Iterator[Any]:
            for sb in sortby:
                if sb is Sortby.is_folder:
                    yield _CompVals.FOLDER if is_dir(node) else _CompVals.FILE
                elif sb is Sortby.ext:
                    yield strxfrm(node.ext or ""),
                elif sb is Sortby.file_name:
                    yield strxfrm(node.name)
                else:
                    never(sb)

        return tuple(cont())

    return comp


def _user_ignored(node: Node, ignores: IgnoreOpts) -> bool:
    return (
        node.name in ignores.name_exact
        or any(fnmatch(node.name, pattern) for pattern in ignores.name_glob)
        or any(fnmatch(node.path, pattern) for pattern in ignores.path_glob)
    )


def _vc_ignored(node: Node, vc: VCStatus) -> bool:
    return not vc.ignored.isdisjoint(node.ancestors | {node.path})


def _gen_spacer(depth: int) -> str:
    return (depth * 2 - 1) * " "


def _paint(
    settings: Settings,
    index: Index,
    selection: Selection,
    qf: QuickFix,
    vc: VCStatus,
    show_hidden: bool,
    current: Optional[str],
) -> Callable[[Node, int], Optional[Render]]:
    icons = settings.view.icons
    context = settings.view.hl_context
    (
        particular_mappings,
        icon_exts,
        mode_pre,
        mode_post,
        ext_exact,
        name_exact,
        name_glob,
    ) = (
        context.particular_mappings,
        context.icon_exts,
        context.mode_pre,
        context.mode_post,
        context.ext_exact,
        context.name_exact,
        context.name_glob,
    )

    def search_icon_hl(node: Node, ignored: bool) -> Optional[str]:
        if ignored:
            return particular_mappings.ignored
        else:
            return icon_exts.get(node.ext or "")

    def search_text_hl(node: Node, ignored: bool) -> Optional[str]:
        if ignored:
            return particular_mappings.ignored

        s_modes = sorted(node.mode)
        for mode in s_modes:
            hl = mode_pre.get(mode)
            if hl:
                return hl

        hl = name_exact.get(node.name)
        if hl:
            return hl

        for pattern, hl in name_glob.items():
            if fnmatch(node.name, pattern):
                return hl

        hl = ext_exact.get(node.ext or "")
        if hl:
            return hl

        for mode in s_modes:
            hl = mode_post.get(mode)
            if hl:
                return hl
        else:
            return mode_post.get(None)

    def gen_status(path: str) -> str:
        selected = (
            icons.status.selected if path in selection else icons.status.not_selected
        )
        active = icons.status.active if path == current else icons.status.inactive
        return f"{selected}{active}"

    def gen_decor_pre(node: Node, depth: int) -> Iterator[str]:
        yield _gen_spacer(depth)
        yield gen_status(node.path)

    def gen_icon(node: Node) -> Iterator[str]:
        yield " "
        if is_dir(node):
            yield icons.folder.open if node.path in index else icons.folder.closed
        else:
            yield (
                icons.name_exact.get(node.name, "")
                or icons.ext_exact.get(node.ext or "", "")
                or next(
                    (v for k, v in icons.name_glob.items() if fnmatch(node.name, k)),
                    icons.default_icon,
                )
            ) if settings.view.use_icons else icons.default_icon
        yield " "

    def gen_name(node: Node) -> Iterator[str]:
        yield node.name.replace(linesep, r"\n")
        if not settings.view.use_icons and is_dir(node):
            yield sep

    def gen_decor_post(node: Node) -> Iterator[str]:
        mode = node.mode
        if Mode.orphan_link in mode:
            yield " "
            yield icons.link.broken
        elif Mode.link in mode:
            yield " "
            yield icons.link.normal

    def gen_badges(path: str) -> Iterator[Badge]:
        qf_count = qf.locations[path]
        stat = vc.status.get(path)
        if qf_count:
            yield Badge(text=f"({qf_count})", group=particular_mappings.quickfix)
        if stat:
            yield Badge(text=f" [{stat}]", group=particular_mappings.version_control)

    def gen_highlights(
        node: Node, pre: str, icon: str, name: str, ignored: bool
    ) -> Iterator[Highlight]:
        icon_begin = len(pre.encode())
        icon_end = icon_begin + len(icon.encode())
        text_begin = icon_end
        text_end = len(name.encode()) + text_begin

        icon_group = search_icon_hl(node, ignored=ignored)
        if icon_group:
            hl = Highlight(group=icon_group, begin=icon_begin, end=icon_end)
            yield hl

        text_group = search_text_hl(node, ignored=ignored)
        if text_group:
            hl = Highlight(group=text_group, begin=text_begin, end=text_end)
            yield hl

    def show(node: Node, depth: int) -> Optional[Render]:
        vc_ignored = _vc_ignored(node, vc=vc)
        user_ignored = _user_ignored(node, ignores=settings.ignores)
        ignored = vc_ignored or user_ignored

        if depth and user_ignored and not show_hidden:
            return None
        else:
            pre = "".join(gen_decor_pre(node, depth=depth))
            icon = "".join(gen_icon(node))
            name = "".join(gen_name(node))
            post = "".join(gen_decor_post(node))

            line = f"{pre}{icon}{name}{post}"
            badges = tuple(gen_badges(node.path))
            highlights = tuple(
                gen_highlights(node, pre=pre, icon=icon, name=name, ignored=ignored)
            )
            return line, highlights, badges

    return show


def render(
    node: Node,
    *,
    settings: Settings,
    index: Index,
    selection: Selection,
    filter_pattern: Optional[FilterPattern],
    qf: QuickFix,
    vc: VCStatus,
    show_hidden: bool,
    current: Optional[str],
) -> Derived:
    show = _paint(
        settings,
        index=index,
        selection=selection,
        qf=qf,
        vc=vc,
        show_hidden=show_hidden,
        current=current,
    )
    comp = _gen_comp(settings.view.sort_by)
    keep_open = {node.path}

    def render(node: Node, *, depth: int, cleared: bool) -> Iterator[NRender]:
        clear = (
            cleared or not filter_pattern or fnmatch(node.name, filter_pattern.pattern)
        )
        rend = show(node, depth)

        if rend:

            def gen_children() -> Iterator[NRender]:
                for child in sorted(node.children.values(), key=comp):
                    yield from render(child, depth=depth + 1, cleared=clear)

            children = tuple(gen_children())
            if clear or children or node.path in keep_open:
                yield (node, *rend)
            yield from iter(children)

    rendered = render(node, depth=0, cleared=False)
    _nodes, _lines, _highlights, _badges = zip(*rendered)
    nodes, lines, highlights, badges = (
        cast(Sequence[Node], _nodes),
        cast(Sequence[str], _lines),
        cast(Sequence[Sequence[Highlight]], _highlights),
        cast(Sequence[Sequence[Badge]], _badges),
    )
    hashed = tuple(map(hash, rendered))
    path_row_lookup = {node.path: idx for idx, node in enumerate(nodes)}
    derived = Derived(
        lines=lines,
        highlights=highlights,
        badges=badges,
        hashed=hashed,
        node_row_lookup=nodes,
        path_row_lookup=path_row_lookup,
    )
    return derived
