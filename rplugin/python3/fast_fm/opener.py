from shutil import which

from .da import call


class OpenError(Exception):
    pass


async def open_gui(path: str) -> None:
    if which("open"):
        ret = await call("open", path)
        if ret.code != 0:
            raise OpenError(ret.err)
    elif which("xdg-open"):
        ret = await call("xdg-open", path)
        if ret.code != 0:
            raise OpenError(ret.err)
    else:
        raise OpenError("⚠️  Error -- cannot find system opener")
