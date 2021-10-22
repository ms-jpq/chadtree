from collections import Counter
from itertools import chain
from os.path import normcase
from pathlib import Path, PurePath
from string import ascii_uppercase
from typing import AbstractSet, Iterator, Mapping

from pynvim import Nvim
from pynvim_pp.api import get_cwd
from std2.string import removeprefix

from ..fs.ops import ancestors
from .types import Markers


def _bookmarks(nvim: Nvim) -> AbstractSet[PurePath]:
    upper = {*ascii_uppercase}
    cwd = get_cwd(nvim)
    marks = nvim.funcs.getmarklist()

    def it() -> Iterator[PurePath]:
        for mark in marks:
            name = str(mark["mark"])
            if (rhs := removeprefix(name, "'")) != name:
                if rhs in upper:
                    file = Path(mark["file"])
                    path = file if file.is_absolute() else cwd / file.expanduser()
                    yield path

    return {*it()}


def _quickfix(nvim: Nvim) -> Mapping[PurePath, int]:
    cwd = get_cwd(nvim)
    ql = nvim.funcs.getqflist()

    def it() -> Iterator[PurePath]:
        for q in ql:
            bufnr = q["bufnr"]
            filename = normcase(nvim.funcs.bufname(bufnr))
            yield cwd / filename

    filenames = tuple(it())
    parents = (ancestor for fullname in filenames for ancestor in ancestors(fullname))
    locations = Counter(chain(filenames, parents))
    return locations


def markers(nvim: Nvim) -> Markers:
    qf = _quickfix(nvim)
    bm = _bookmarks(nvim)
    markers = Markers(quick_fix=qf, bookmarks=bm)
    return markers
