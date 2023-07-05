from collections import UserString
from enum import IntEnum, auto
from fnmatch import fnmatch
from locale import strxfrm
from os.path import extsep, sep
from pathlib import PurePath
from typing import (
    Any,
    Callable,
    Iterator,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Union,
    cast,
)

from pynvim_pp.lib import encode
from std2.platform import OS, os
from std2.types import never

from ..fs.cartographer import is_dir, user_ignored
from ..fs.types import Mode, Node
from ..nvim.types import Markers
from ..settings.types import Settings
from ..state.types import FilterPattern, Index, Selection
from ..version_ctl.types import VCStatus
from .ops import encode_for_display
from .types import Badge, Derived, Highlight, Sortby


class _CompVals(IntEnum):
    FOLDER = auto()
    FILE = auto()


_Str = Union[str, UserString]
_Render = Tuple[str, Sequence[Highlight], Sequence[Badge]]
_NRender = Tuple[Node, str, Sequence[Highlight], Sequence[Badge]]


class _str(UserString):
    def __lt__(self, _: _Str) -> bool:
        return False

    def __gt__(self, _: _Str) -> bool:
        return True


def _suffixx(path: PurePath) -> _Str:
    if path.suffix:
        return strxfrm(path.suffix)
    elif path.stem.startswith(extsep):
        return strxfrm(path.stem)
    else:
        return _str("")


def _gen_comp(sortby: Sequence[Sortby]) -> Callable[[Node], Any]:
    def comp(node: Node) -> Sequence[Any]:
        def cont() -> Iterator[Any]:
            for sb in sortby:
                if sb is Sortby.is_folder:
                    yield _CompVals.FOLDER if is_dir(node) else _CompVals.FILE
                elif sb is Sortby.ext:
                    yield "" if is_dir(node) else _suffixx(node.path)
                elif sb is Sortby.file_name:
                    yield strxfrm(node.path.name)
                else:
                    never(sb)

        return tuple(cont())

    return comp


def _vc_ignored(node: Node, vc: VCStatus) -> bool:
    pointer = node.pointed or node.path
    return not vc.ignored.isdisjoint({pointer} | {*map(PurePath, pointer.parents)})


def _gen_spacer(depth: int) -> str:
    return (depth * 2 - 1) * " "


def _paint(
    settings: Settings,
    index: Index,
    selection: Selection,
    markers: Markers,
    vc: VCStatus,
    show_hidden: bool,
    current: Optional[PurePath],
) -> Callable[[Node, int], Optional[_Render]]:
    icons = settings.view.icons
    context = settings.view.hl_context

    def search_icon_hl(node: Node, ignored: bool) -> Optional[str]:
        if ignored:
            return context.particular_mappings.ignored
        else:
            return context.icon_exts.get(node.path.suffix)

    def search_text_hl(node: Node, ignored: bool) -> Optional[str]:
        if ignored:
            return context.particular_mappings.ignored

        s_modes = sorted(node.mode)
        for mode in s_modes:
            if os is OS.windows and mode is Mode.other_writable:
                pass
            elif hl := context.mode_pre.get(mode):
                return hl

        if hl := context.name_exact.get(node.path.name):
            return hl

        for pattern, hl in context.name_glob.items():
            if fnmatch(node.path.name, pattern):
                return hl

        if hl := context.ext_exact.get(node.path.suffix):
            return hl

        for mode in s_modes:
            if hl := context.mode_post.get(mode):
                return hl
        else:
            return context.mode_post.get(None)

    def gen_status(path: PurePath) -> str:
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
                icons.name_exact.get(node.path.name, "")
                or icons.ext_exact.get(node.path.suffix, "")
                or next(
                    (
                        v
                        for k, v in icons.name_glob.items()
                        if fnmatch(node.path.name, k)
                    ),
                    icons.default_icon,
                )
            ) if settings.view.use_icons else icons.default_icon
        yield " "

    def gen_name(node: Node) -> Iterator[str]:
        yield encode_for_display(node.path.name)
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

    def gen_badges(path: PurePath) -> Iterator[Badge]:
        if marks := markers.bookmarks.get(path):
            ordered = "".join(sorted(marks))
            yield Badge(
                text=f"<{ordered}>",
                group=context.particular_mappings.bookmarks,
            )

        if qf_count := markers.quick_fix.get(path):
            yield Badge(
                text=f"({qf_count})",
                group=context.particular_mappings.quickfix,
            )

        if stat := vc.status.get(path):
            yield Badge(
                text=f" [{stat}]",
                group=context.particular_mappings.version_control,
            )

    def gen_highlights(
        node: Node, pre: str, icon: str, name: str, ignored: bool
    ) -> Iterator[Highlight]:
        icon_begin = len(encode(pre))
        icon_end = icon_begin + len(encode(icon))
        text_begin = icon_end
        text_end = len(encode(name)) + text_begin

        if icon_group := search_icon_hl(node, ignored=ignored):
            hl = Highlight(group=icon_group, begin=icon_begin, end=icon_end)
            yield hl

        if text_group := search_text_hl(node, ignored=ignored):
            hl = Highlight(group=text_group, begin=text_begin, end=text_end)
            yield hl

    def show(node: Node, depth: int) -> Optional[_Render]:
        _user_ignored = user_ignored(node, ignores=settings.ignores)
        vc_ignored = _vc_ignored(node, vc=vc)
        ignored = vc_ignored or _user_ignored

        if depth and _user_ignored and not show_hidden:
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
    markers: Markers,
    vc: VCStatus,
    show_hidden: bool,
    current: Optional[PurePath],
) -> Derived:
    show = _paint(
        settings,
        index=index,
        selection=selection,
        markers=markers,
        vc=vc,
        show_hidden=show_hidden,
        current=current,
    )
    comp = _gen_comp(settings.view.sort_by)
    keep_open = {node.path}

    def render(node: Node, *, depth: int, cleared: bool) -> Iterator[_NRender]:
        clear = (
            cleared
            or not filter_pattern
            or fnmatch(node.path.name, filter_pattern.pattern)
        )

        if rend := show(node, depth):

            def gen_children() -> Iterator[_NRender]:
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
    hashed = tuple(str(hash(zipped)) for zipped in zip(lines, highlights, badges))
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
