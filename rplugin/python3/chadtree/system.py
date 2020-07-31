from shutil import which
from typing import Iterable

from .da import call


class SystemIntegrationError(Exception):
    pass


async def open_gui(path: str) -> None:
    if which("open"):
        ret = await call("open", path)
        if ret.code != 0:
            raise SystemIntegrationError(ret.err)
    elif which("xdg-open"):
        ret = await call("xdg-open", path)
        if ret.code != 0:
            raise SystemIntegrationError(ret.err)
    else:
        raise SystemIntegrationError("⚠️  Error -- cannot find system opener")


async def trash(paths: Iterable[str]) -> None:
    if which("trash"):
        ret = await call("trash", *paths)
        if ret.code != 0:
            raise SystemIntegrationError(ret.err)
    else:
        raise SystemIntegrationError("⚠️  Error -- cannot find trash program")
