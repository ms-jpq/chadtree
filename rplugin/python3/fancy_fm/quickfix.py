from collections import Counter, defaultdict
from typing import Iterator, Sequence

from pynvim import Nvim

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
    count = Counter(filenames)
    locations = defaultdict(int, count)
    qf = QuickFix(locations=locations)
    return qf
