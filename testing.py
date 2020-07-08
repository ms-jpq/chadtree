#!/usr/bin/env python3

from asyncio import run
from os import getcwd

from rplugin.python3.fm.fs import parse
from rplugin.python3.fm.render import dparse, render


async def main() -> None:
    cwd = getcwd()
    n = parse(cwd, max_depth=2)
    d = dparse(n)
    r = render(d)
    print(*r, sep="\n")

    pass


run(main())
