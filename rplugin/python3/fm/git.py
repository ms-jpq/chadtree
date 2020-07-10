from asyncio import gather
from os.path import sep
from typing import Iterable, Tuple

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


async def stat() -> Iterable[Tuple[str, str]]:
    ret = await call("git", "status", "--ignored", "--porcelain", "-z")
    if ret.code != 0:
        raise GitError(ret.err)
    else:
        entries = (
            (prefix, file.rstrip(sep))
            for prefix, file in ((line[:2], line[3:]) for line in ret.out.split("\0"))
        )
        return entries


def parse(root: str, stats: Tuple[str, str]) -> GitStatus:
    return GitStatus()


async def status() -> GitStatus:
    try:
        r, stats = await gather(root(), stat())
        return parse(r, stats)
    except GitError:
        return GitStatus()
