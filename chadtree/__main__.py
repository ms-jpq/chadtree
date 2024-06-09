from argparse import ArgumentParser, Namespace
from asyncio import run as arun
from concurrent.futures import ThreadPoolExecutor
from contextlib import nullcontext, redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path, PurePath
from subprocess import DEVNULL, STDOUT, CalledProcessError, run
from sys import (
    executable,
    exit,
    getswitchinterval,
    setswitchinterval,
    stderr,
    version_info,
)
from textwrap import dedent
from typing import Any, Union
from webbrowser import open as open_w

from .consts import GIL_SWITCH, IS_WIN, MIGRATION_URI, REQUIREMENTS, RT_DIR, RT_PY

setswitchinterval(min(getswitchinterval(), GIL_SWITCH))

try:
    from typing import Literal

    if version_info < (3, 8, 2):
        raise ImportError()
except ImportError:
    msg = "For python < 3.8.2 please install using the branch -- legacy"
    print(msg, file=stderr)
    open_w(MIGRATION_URI)
    exit(1)


def _socket(arg: str) -> Any:
    if arg.startswith("localhost:"):
        host, _, port = arg.rpartition(":")
        return host, int(port)
    else:
        return PurePath(arg)


def parse_args() -> Namespace:
    parser = ArgumentParser()

    sub_parsers = parser.add_subparsers(dest="command", required=True)

    with nullcontext(sub_parsers.add_parser("run")) as p:
        p.add_argument("--ppid", type=int)
        p.add_argument("--socket", required=True, type=_socket)
        p.add_argument("--xdg")

    with nullcontext(sub_parsers.add_parser("deps")) as p:
        p.add_argument("--nvim", action="store_true")
        p.add_argument("--xdg", nargs="?")

    return parser.parse_args()


args = parse_args()
command: Union[Literal["deps"], Literal["run"]] = args.command

_XDG = Path(args.xdg) if args.xdg is not None else None

_RT_DIR = _XDG / "chadrt" if _XDG else RT_DIR
_RT_PY = (
    (_RT_DIR / "Scripts" / "python.exe" if IS_WIN else _RT_DIR / "bin" / "python3")
    if _XDG
    else RT_PY
)
_LOCK_FILE = _RT_DIR / "requirements.lock"
_EXEC_PATH = Path(executable)
_EXEC_PATH = _EXEC_PATH.parent.resolve(strict=True) / _EXEC_PATH.name
_REQ = REQUIREMENTS.read_text()

_IN_VENV = _RT_PY == _EXEC_PATH


if command == "deps":
    assert not _IN_VENV

    io_out = StringIO()
    try:
        from venv import EnvBuilder

        print("...", flush=True)
        with redirect_stdout(io_out), redirect_stderr(io_out):
            EnvBuilder(
                system_site_packages=False,
                with_pip=True,
                upgrade=True,
                symlinks=not IS_WIN,
                clear=True,
            ).create(_RT_DIR)
    except (ImportError, CalledProcessError):
        msg = "Please install python3-venv separately. (apt, yum, apk, etc)"
        print(msg, io_out.getvalue(), file=stderr)
        exit(1)
    else:
        quiet = () if stderr.isatty() else ("--quiet",)
        proc = run(
            (
                _RT_PY,
                "-m",
                "pip",
                *quiet,
                "install",
                "--upgrade",
                "--requirement",
                REQUIREMENTS,
            ),
            stdin=DEVNULL,
            stderr=STDOUT,
        )
        if proc.returncode:
            print("Installation failed, check :message", file=stderr)
            exit(proc.returncode)
        else:
            _LOCK_FILE.write_text(_REQ)
            msg = """
            ---
            You can now use :CHADopen
            """
            print(dedent(msg), file=stderr)

elif command == "run":
    try:
        lock = _LOCK_FILE.read_text()
    except Exception:
        lock = ""
    try:
        if not _IN_VENV:
            raise ImportError()
        elif lock != _REQ:
            raise ImportError()
        else:
            import pynvim_pp
            import yaml

            from .client import init
    except ImportError as e:
        print(e)
        msg = """
        Please update dependencies using :CHADdeps
        -
        -
        Dependencies will be installed privately inside `chadtree/.vars`
        `rm -rf chadtree/` will cleanly remove everything
        """
        msg = dedent(msg)
        print(msg, end="", file=stderr)
        exit(1)
    else:
        with ThreadPoolExecutor() as th:
            arun(init(args.socket, ppid=args.ppid, th=th))


else:
    assert False
