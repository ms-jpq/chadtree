from typing import Sequence

from .da import call


async def ignored() -> Sequence[str]:
    ret = await call("git", "status", "--ignored", "--short", "-z")
    if ret.code != 0:
        return ()
    else:
        files = tuple(line.split(" ", 1)[1] for line in ret.out.split("\0"))
        return files
