from collections import Counter, defaultdict
from itertools import chain
from typing import Iterator, Sequence

from pynvim import Nvim

from .fs import ancestors
from .nvim import call
from .types import QuickFix


async def quickfix(nvim: Nvim) -> QuickFix:
    def cont() -> Sequence[str]:
        ql = nvim.funcs.getqflist()

        def c() -> Iterator[str]:
            for q in ql:
                bufnr = q["bufnr"]
                filename = nvim.funcs.bufname(bufnr)
                yield filename

        return tuple(c())

    filenames = await call(nvim, cont)
    parents = (ancestor for filename in filenames for ancestor in ancestors(filename))
    count = Counter(chain(filenames, parents))
    locations = defaultdict(int, count)
    qf = QuickFix(locations=locations)
    return qf
