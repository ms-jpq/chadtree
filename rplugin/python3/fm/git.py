from asyncio import gather
from typing import Sequence
from shutil import which

from .da import call
from .types import GitStatus


async def ignored() -> Sequence[str]:
    ret = await call("git", "status", "--ignored", "--short", "-z")
    if ret.code != 0:
        return ()
    else:
        files = tuple(line.split(" ", 1)[1] for line in ret.out.split("\0"))
        return files


async def modified() -> Sequence[str]:
    ret = await call("git", "diff", "--name-only", "-z")
    if ret.code != 0:
        return ()
    else:
        files = ret.out.split("\0")
        return files


async def staged() -> Sequence[str]:
    ret = await call("git", "diff", "--name-only", "--cached", "-z")
    if ret.code != 0:
        return ()
    else:
        files = ret.out.split("\0")
        return files


async def status() -> GitStatus:
    if which("git"):
        i, m, s = await gather(ignored(), modified(), staged())
        return GitStatus(ignored=i, modified=m, staged=s)
    else:
        return GitStatus()
