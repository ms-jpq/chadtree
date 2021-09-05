from collections import Counter
from itertools import chain
from pathlib import PurePath
from typing import Iterator

from pynvim import Nvim
from pynvim_pp.api import get_cwd

from ..fs.ops import ancestors
from .types import QuickFix


def quickfix(nvim: Nvim) -> QuickFix:
    cwd = PurePath(get_cwd(nvim))
    ql = nvim.funcs.getqflist()

    def it() -> Iterator[PurePath]:
        for q in ql:
            bufnr = q["bufnr"]
            filename = nvim.funcs.bufname(bufnr)
            yield cwd / filename

    filenames = tuple(it())
    parents = (ancestor for fullname in filenames for ancestor in ancestors(fullname))
    locations = Counter(chain(filenames, parents))
    qf = QuickFix(locations=locations)
    return qf
