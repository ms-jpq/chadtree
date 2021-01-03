from shutil import which
from typing import Iterable

from std2.asyncio.subprocess import call
from .localization import LANG


class SystemIntegrationError(Exception):
    ...


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
        raise SystemIntegrationError(LANG("sys_open_err"))


async def trash(paths: Iterable[str]) -> None:
    if which("trash"):
        ret = await call("trash", *paths)
        if ret.code != 0:
            raise SystemIntegrationError(ret.err)
    else:
        raise SystemIntegrationError(LANG("sys_trash_err"))
