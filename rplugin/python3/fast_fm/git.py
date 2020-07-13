from asyncio import gather
from os.path import join, sep
from shutil import which
from typing import Iterable, Tuple

from .da import call
from .types import VCStatus


class GitError(Exception):
    pass


async def root() -> str:
    ret = await call("git", "rev-parse", "--show-toplevel")
    if ret.code != 0:
        raise GitError(ret.err)
    else:
        return ret.out.rstrip()


async def stat() -> Iterable[Tuple[str, str]]:
    ret = await call("git", "status", "--ignored", "--renames", "--porcelain", "-z")
    if ret.code != 0:
        raise GitError(ret.err)
    else:
        entries = (
            (prefix, file.rstrip(sep))
            for prefix, file in ((line[:2], line[3:]) for line in ret.out.split("\0"))
        )
        return entries


def parse(root: str, stats: Iterable[Tuple[str, str]]) -> VCStatus:
    ignored = set()
    status = {}
    for stat, name in stats:
        path = join(root, name)
        status[path] = stat
        if "!" in stat:
            ignored.add(path)
    return VCStatus(ignored=ignored, status=status)


async def status() -> VCStatus:
    if which("git"):
        try:
            r, stats = await gather(root(), stat())
            return parse(r, stats)
        except GitError:
            return VCStatus()
    else:
        return VCStatus()
