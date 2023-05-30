from asyncio import gather
from collections import Counter
from itertools import chain
from pathlib import PurePath
from typing import AbstractSet, Mapping, MutableMapping, MutableSet, Sequence, cast

from pynvim_pp.atomic import Atomic
from pynvim_pp.buffer import Buffer
from pynvim_pp.nvim import Marker, Nvim
from pynvim_pp.types import NoneType

from ..fs.ops import ancestors
from .types import Markers


async def _bookmarks() -> Mapping[PurePath, AbstractSet[Marker]]:
    acc: MutableMapping[PurePath, MutableSet[Marker]] = {}
    bookmarks = await Nvim.list_bookmarks()
    for marker, (path, _, _) in bookmarks.items():
        if path:
            for marked_path in chain((path,), ancestors(path)):
                marks = acc.setdefault(marked_path, set())
                marks.add(marker)

    return acc


async def _quickfix() -> Mapping[PurePath, int]:
    qflist = cast(Sequence[Mapping[str, int]], await Nvim.fn.getqflist(NoneType))

    atomic = Atomic()
    for q in qflist:
        bufnr = q["bufnr"]
        buf = Buffer.from_int(bufnr)
        atomic.buf_get_name(buf)

    bufnames = cast(Sequence[str], await atomic.commit(NoneType))
    filenames = tuple(map(PurePath, bufnames))
    parents = (ancestor for fullname in filenames for ancestor in ancestors(fullname))
    locations = Counter(chain(filenames, parents))

    return locations


async def markers() -> Markers:
    qf, bm = await gather(_quickfix(), _bookmarks())
    markers = Markers(quick_fix=qf, bookmarks=bm)
    return markers
