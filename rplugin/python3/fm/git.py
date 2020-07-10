from asyncio import gather
from shutil import which
from typing import Set

from .da import call
from .types import GitStatus


async def ignored() -> Set[str]:
    ret = await call("git", "status", "--ignored", "--porcelain", "-z")
    if ret.code != 0:
        return set()
    else:
        files = (
            file
            for prefix, file in (line.split(" ", 1) for line in ret.out.split("\0"))
            if prefix == "!!"
        )
        return set(files)


async def modified() -> Set[str]:
    ret = await call("git", "diff", "--name-only", "-z")
    if ret.code != 0:
        return set()
    else:
        files = ret.out.split("\0")
        return set(files)


async def staged() -> Set[str]:
    ret = await call("git", "diff", "--name-only", "--cached", "-z")
    if ret.code != 0:
        return set()
    else:
        files = ret.out.split("\0")
        return set(files)


async def status() -> GitStatus:
    if which("git"):
        i, m, s = await gather(ignored(), modified(), staged())
        return GitStatus(ignored=i, modified=m, staged=s)
    else:
        return GitStatus()
