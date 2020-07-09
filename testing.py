#!/usr/bin/env python3

from asyncio import run
from os import getcwd

from rplugin.python3.fm.cartographer import new
from rplugin.python3.fm.render import dparse, render


async def main() -> None:
    cwd = getcwd()
    n = new(cwd, index={cwd})
    r = render(n)
    print(r, sep="\n")

    pass


run(main())
