from collections import Counter, defaultdict
from itertools import chain
from os.path import join
from typing import Iterator

from pynvim import Nvim
from pynvim_pp.api import get_cwd

from ..fs.ops import ancestors
from .types import QuickFix


def quickfix(nvim: Nvim) -> QuickFix:
    cwd = get_cwd(nvim)
    ql = nvim.funcs.getqflist()

    def it() -> Iterator[str]:
        for q in ql:
            bufnr = q["bufnr"]
            filename = nvim.funcs.bufname(bufnr)
            yield join(cwd, filename)

    filenames = tuple(it())
    parents = (ancestor for fullname in filenames for ancestor in ancestors(fullname))
    count = Counter(chain(filenames, parents))
    locations = defaultdict(int, count)
    qf = QuickFix(locations=locations)
    return qf
