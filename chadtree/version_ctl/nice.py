import sys
from asyncio import create_task, gather
from contextlib import suppress
from functools import lru_cache
from os import environ
from pathlib import PurePath
from shutil import which
from subprocess import CalledProcessError
from typing import Awaitable, Optional, Sequence

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


@lru_cache(maxsize=None)
def very_nice() -> Awaitable[Sequence[str]]:
    async def cont() -> Sequence[str]:
        if tp := which("taskpolicy"):
            run: Sequence[str] = (tp, "-b", "--")
            try:
                await call(*run, "true")
            except (OSError, CalledProcessError):
                return ()
            else:
                return run
        elif (sd := which("systemd-notify")) and (sr := which("systemd-run")):
            run = (
                sr,
                "--quiet",
                "--collect",
                "--user",
                "--pipe",
                "--same-dir",
                "--wait",
                "--service-type",
                "exec",
                "--nice",
                "19",
                "--property",
                "CPUWeight=69",
                "--",
            )
            try:
                await gather(call(sd, "--booted"), call(*run, "true"))
            except (OSError, CalledProcessError):
                return ()
            else:
                return run
        else:
            return ()

    return create_task(cont())


def _nice() -> None:
    with suppress(PermissionError):
        nice(19)


async def nice_call(
    argv: Sequence[AnyPath],
    stdin: Optional[bytes] = None,
    cwd: Optional[PurePath] = None,
) -> str:
    prefix = await very_nice()
    proc = await call(
        *prefix,
        *argv,
        cwd=cwd,
        env=_ENV,
        preexec_fn=_nice,
        creationflags=BELOW_NORMAL_PRIORITY_CLASS,
    )
    return decode(proc.stdout)
