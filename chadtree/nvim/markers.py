from collections import Counter
from itertools import chain
from pathlib import PurePath
from typing import AbstractSet, Iterator, Mapping, MutableMapping, MutableSet

from pynvim import Nvim
from pynvim_pp.api import get_cwd, list_bookmarks
from pynvim_pp.lib import resolve_path

from ..fs.ops import ancestors
from .types import Markers


def _bookmarks(nvim: Nvim) -> Mapping[PurePath, AbstractSet[str]]:
    acc: MutableMapping[PurePath, MutableSet[str]] = {}
    for mark_id, path in list_bookmarks(nvim):
        for marked_path in chain((path,), ancestors(path)):
            marks = acc.setdefault(marked_path, set())
            marks.add(mark_id)

    return acc


def _quickfix(nvim: Nvim) -> Mapping[PurePath, int]:
    def it() -> Iterator[PurePath]:
        cwd = get_cwd(nvim)
        for q in nvim.funcs.getqflist():
            bufnr = q["bufnr"]
            bufname = nvim.funcs.bufname(bufnr)
            if resolved := resolve_path(cwd, path=bufname):
                yield resolved

    filenames = tuple(it())
    parents = (ancestor for fullname in filenames for ancestor in ancestors(fullname))
    locations = Counter(chain(filenames, parents))

    return locations


def markers(nvim: Nvim) -> Markers:
    qf = _quickfix(nvim)
    bm = _bookmarks(nvim)
    markers = Markers(quick_fix=qf, bookmarks=bm)
    return markers
