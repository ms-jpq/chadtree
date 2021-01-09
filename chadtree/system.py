from shutil import which
from subprocess import DEVNULL, PIPE, run
from typing import Iterable

from .localization import LANG


class SystemIntegrationError(Exception):
    ...


def open_gui(path: str) -> None:
    if which("open"):
        ret = run(("open", path), stdin=DEVNULL, stdout=DEVNULL, stderr=PIPE)
        if ret.returncode != 0:
            raise SystemIntegrationError(ret.stderr)
    elif which("xdg-open"):
        ret = run(("xdg-open", path), stdin=DEVNULL, stdout=DEVNULL, stderr=PIPE)
        if ret.returncode != 0:
            raise SystemIntegrationError(ret.stderr)
    else:
        raise SystemIntegrationError(LANG("sys_open_err"))


def trash(paths: Iterable[str]) -> None:
    if which("trash"):
        ret = run(("trash", *paths), stdin=DEVNULL, stdout=DEVNULL, stderr=PIPE)
        if ret.returncode != 0:
            raise SystemIntegrationError(ret.stderr)
    else:
        raise SystemIntegrationError(LANG("sys_trash_err"))
