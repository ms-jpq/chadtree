from asyncio import create_subprocess_shell
from asyncio.subprocess import DEVNULL, PIPE
from typing import Set


class SearchError(Exception):
    pass


async def search(args: str, cwd: str) -> Set[str]:
    proc = await create_subprocess_shell(
        args, stdin=DEVNULL, stdout=PIPE, stderr=PIPE, cwd=cwd
    )
    stdout, stderr = await proc.communicate()
    out, err = stdout.decode(), stderr.decode()
    if err:
        raise SearchError(err)
    else:
        return {*out.splitlines()}
