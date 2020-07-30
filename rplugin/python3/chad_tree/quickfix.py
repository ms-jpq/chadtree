from asyncio import gather
from collections import Counter, defaultdict
from itertools import chain
from os.path import join
from typing import Iterator, Sequence

from pynvim import Nvim

from .fs import ancestors
from .nvim import call, getcwd
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

    cwd, filenames = await gather(getcwd(nvim), call(nvim, cont))
    full_names = tuple(join(cwd, filename) for filename in filenames)
    parents = (ancestor for fullname in full_names for ancestor in ancestors(fullname))
    count = Counter(chain(full_names, parents))
    locations = defaultdict(int, count)
    qf = QuickFix(locations=locations)
    return qf
