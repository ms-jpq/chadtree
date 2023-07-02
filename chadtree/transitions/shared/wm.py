from contextlib import suppress
from math import inf
from pathlib import PurePath
from typing import (
    AbstractSet,
    AsyncIterator,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Union,
    cast,
)
from urllib.parse import urlsplit

from pynvim_pp.atomic import Atomic
from pynvim_pp.buffer import Buffer
from pynvim_pp.keymap import Keymap
from pynvim_pp.lib import resolve_path
from pynvim_pp.nvim import Nvim
from pynvim_pp.tabpage import Tabpage
from pynvim_pp.types import ExtData, NoneType
from pynvim_pp.window import Window

from ...consts import FM_FILETYPE, URI_SCHEME
from ...fs.ops import ancestors
from ...settings.types import Settings


def _is_chadtree_buf_name(name: str) -> bool:
    with suppress(ValueError):
        uri = urlsplit(name)
        return uri.scheme == URI_SCHEME
    return False


async def is_fm_buffer(buf: Buffer) -> bool:
    ft = await buf.filetype()
    if ft == FM_FILETYPE:
        return True
    elif name := await buf.get_name():
        return _is_chadtree_buf_name(name)

    return False


async def is_fm_window(win: Window) -> bool:
    buf = await win.get_buf()
    return await is_fm_buffer(buf)


async def find_windows_in_tab(
    last_used: Mapping[ExtData, None], no_secondary: bool
) -> AsyncIterator[Window]:
    ordering = {win_id: idx for idx, win_id in enumerate(reversed(last_used.keys()))}
    tab = await Tabpage.get_current()
    wins = await tab.list_wins()

    atomic = Atomic()
    for win in wins:
        atomic.win_get_position(win)
    pos = cast(Sequence[Tuple[int, int]], await atomic.commit(NoneType))
    positions = {win.data: rc for win, rc in zip(wins, pos)}

    def key_by(win: Window) -> Tuple[float, float, float]:
        """
        -> sort by last_used, then row, then col
        """

        order = ordering.get(win.data, inf)
        row, col = positions.get(win.data, (inf, inf))
        return order, col, row

    ordered = sorted(wins, key=key_by)

    for win in ordered:
        is_preview = await win.opts.get(bool, "previewwindow")
        buf = await win.get_buf()
        ft = await buf.filetype()
        is_secondary = is_preview or ft == "qf"
        if not is_secondary or not no_secondary:
            yield win


async def find_fm_windows() -> AsyncIterator[Tuple[Window, Buffer]]:
    for win in await Window.list():
        buf = await win.get_buf()
        if await is_fm_buffer(buf):
            yield win, buf


async def find_fm_windows_in_tab(
    last_used: Mapping[ExtData, None]
) -> AsyncIterator[Window]:
    async for win in find_windows_in_tab(last_used, no_secondary=True):
        buf = await win.get_buf()
        if await is_fm_buffer(buf):
            yield win


async def find_non_fm_windows_in_tab(
    last_used: Mapping[ExtData, None]
) -> AsyncIterator[Window]:
    async for win in find_windows_in_tab(last_used, no_secondary=True):
        buf = await win.get_buf()
        if not await is_fm_buffer(buf):
            yield win


async def find_window_with_file_in_tab(
    last_used: Mapping[ExtData, None], file: PurePath
) -> AsyncIterator[Window]:
    async for win in find_windows_in_tab(last_used, no_secondary=True):
        buf = await win.get_buf()
        if name := await buf.get_name():
            if PurePath(name) == file:
                yield win


async def find_fm_buffers() -> AsyncIterator[Buffer]:
    for buf in await Buffer.list(listed=True):
        if await is_fm_buffer(buf):
            yield buf


async def find_buffers_with_file(file: PurePath) -> AsyncIterator[Buffer]:
    for buf in await Buffer.list(listed=True):
        if name := await buf.get_name():
            if PurePath(name) == file:
                yield buf


async def find_current_buffer_path() -> Optional[PurePath]:
    buf = await Buffer.get_current()
    if name := await buf.get_name():
        if not _is_chadtree_buf_name(name):
            return await resolve_path(None, path=name)

    return None


async def new_fm_buffer(settings: Settings) -> Buffer:
    buf = await Buffer.create(
        listed=False, scratch=True, wipe=False, nofile=True, noswap=True
    )
    await buf.opts.set("modifiable", val=False)
    await buf.opts.set("filetype", val=FM_FILETYPE)
    await buf.opts.set("undolevels", val=-1)

    km = Keymap()
    _ = km.n("{") << f"{settings.page_increment}g<up>"
    _ = km.n("}") << f"{settings.page_increment}g<down>"
    for function, mappings in settings.keymap.items():
        for mapping in mappings:
            _ = (
                km.n(mapping, noremap=True, silent=True, nowait=True)
                << f"<cmd>lua {function}(false)<cr>"
            )
            _ = (
                km.v(mapping, noremap=True, silent=True, nowait=True)
                << rf"<c-\><c-n><cmd>lua {function}(true)<cr>"
            )

    await km.drain(buf=buf).commit(NoneType)
    return buf


async def new_window(
    *,
    last_used: Mapping[ExtData, None],
    win_local: Mapping[str, Union[bool, str]],
    open_left: bool,
    width: Optional[int],
) -> Window:
    split_r = await Nvim.opts.get(bool, "splitright")

    wins = [win async for win in find_windows_in_tab(last_used, no_secondary=False)]
    focus_win = wins[0] if open_left else wins[-1]
    direction = False if open_left else True

    await Nvim.opts.set("splitright", val=direction)
    await Window.set_current(focus_win)
    await Nvim.exec(f"{width}vnew" if width else "vnew")
    await Nvim.opts.set("splitright", val=split_r)

    win = await Window.get_current()
    buf = await win.get_buf()
    for key, val in win_local.items():
        await win.opts.set(key, val=val)
    await buf.opts.set("bufhidden", val="wipe")
    return win


async def resize_fm_windows(last_used: Mapping[ExtData, None], width: int) -> None:
    async for win in find_fm_windows_in_tab(last_used):
        await win.set_width(width)


async def kill_buffers(
    last_used: Mapping[ExtData, None],
    paths: AbstractSet[PurePath],
    reopen: Mapping[PurePath, PurePath],
) -> Mapping[Window, PurePath]:
    active = (
        {
            await win.get_buf(): win
            async for win in find_non_fm_windows_in_tab(
                last_used,
            )
        }
        if reopen
        else {}
    )

    async def cont() -> AsyncIterator[Tuple[Window, PurePath]]:
        for buf in await Buffer.list(listed=True):
            if bufname := await buf.get_name():
                name = PurePath(bufname)
                buf_paths = ancestors(name) | {name}

                if not buf_paths.isdisjoint(paths):
                    if (
                        reopen
                        and (win := active.get(buf))
                        and (new_path := reopen.get(name))
                    ):
                        tmp = await Buffer.create(
                            listed=False,
                            scratch=True,
                            wipe=True,
                            nofile=True,
                            noswap=True,
                        )
                        await win.set_buf(tmp)
                        yield win, new_path
                    await buf.delete()

    return {win: path async for win, path in cont()}
