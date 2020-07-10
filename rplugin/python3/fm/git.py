from asyncio import gather
from functools import partial
from os.path import join
from typing import Iterable

from .da import call
from .types import GitStatus


class GitError(Exception):
    pass


async def root() -> str:
    ret = await call("git", "rev-parse", "--show-toplevel")
    if ret.code != 0:
        raise GitError(ret.err)
    else:
        return ret.out


async def ignored() -> Iterable[str]:
    ret = await call("git", "status", "--ignored", "--porcelain", "-z")
    if ret.code != 0:
        raise GitError(ret.err)
    else:
        entries = (
            file.rstrip("/")
            for prefix, file in (line.split(" ", 1) for line in ret.out.split("\0"))
            if prefix == "!!"
        )
        return entries


async def modified() -> Iterable[str]:
    ret = await call("git", "diff", "--name-only", "-z")
    if ret.code != 0:
        raise GitError(ret.err)
    else:
        files = ret.out.split("\0")
        return files


async def staged() -> Iterable[str]:
    ret = await call("git", "diff", "--name-only", "--cached", "-z")
    if ret.code != 0:
        raise GitError(ret.err)
    else:
        files = ret.out.split("\0")
        return files


async def status() -> GitStatus:
    try:
        r, i, m, s = await gather(root(), ignored(), modified(), staged())
        jj = partial(join, r)
        ii = set(map(jj, i))
        mm = set(map(jj, m))
        ss = set(map(jj, s))
        return GitStatus(ignored=ii, modified=mm, staged=ss)
    except GitError:
        return GitStatus()
