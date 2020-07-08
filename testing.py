#!/usr/bin/env python3

from asyncio import run
from rplugin.python3.fm.fs import tree


async def main() -> None:
    tr = tree()
    print(tr)


run(main())
