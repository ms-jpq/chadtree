import sys
from contextlib import suppress
from os import environ
from pathlib import PurePath
from typing import Optional, Sequence

from pynvim_pp.lib import decode
from std2.asyncio.subprocess import call
from std2.pathlib import AnyPath

if sys.platform == "win32":
    from subprocess import BELOW_NORMAL_PRIORITY_CLASS

    nice = lambda _: None
else:
    from os import nice

    BELOW_NORMAL_PRIORITY_CLASS = 0


_ENV = {**environ, "LC_ALL": "C"}


def _nice() -> None:
    with suppress(PermissionError):
        nice(19)


async def nice_call(
    argv: Sequence[AnyPath],
    stdin: Optional[bytes] = None,
    cwd: Optional[PurePath] = None,
) -> str:
    proc = await call(
        *argv,
        cwd=cwd,
        stdin=stdin,
        env=_ENV,
        preexec_fn=_nice,
        creationflags=BELOW_NORMAL_PRIORITY_CLASS,
    )
    return decode(proc.stdout)
