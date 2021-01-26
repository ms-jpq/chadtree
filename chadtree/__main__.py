from argparse import ArgumentParser, Namespace
from subprocess import DEVNULL, run
from sys import executable, path, stderr, stdout, version_info
from textwrap import dedent
from typing import Union
from webbrowser import open as open_w

from .consts import (
    DEPS_LOCK,
    DEPS_LOCK_XDG,
    MIGRATION_URI,
    REQUIREMENTS,
    RT_DIR,
    RT_DIR_XDG,
)

if version_info < (3, 8, 2):
    msg = "For python < 3.8.2 please install using the branch -- legacy"
    print(msg, end="", file=stderr)
    open_w(MIGRATION_URI)


from typing import Literal


def parse_args() -> Namespace:
    parser = ArgumentParser()

    sub_parsers = parser.add_subparsers(dest="command", required=True)

    s_run = sub_parsers.add_parser("run")
    s_run.add_argument("--socket", required=True)
    s_run.add_argument("--xdg", action="store_true")

    s_deps = sub_parsers.add_parser("deps")
    s_deps.add_argument("--xdg", action="store_true")

    return parser.parse_args()


args = parse_args()
command: Union[Literal["deps"], Literal["run"]] = args.command

_RT_DIR = RT_DIR_XDG if args.xdg else RT_DIR

_RT_DIR.mkdir(parents=True, exist_ok=True)
_DEPS_LOCK = DEPS_LOCK_XDG if args.xdg else DEPS_LOCK
path.append(str(_RT_DIR))


if command == "deps":
    try:
        import pip
    except ImportError:
        print("Please install pip separately.", file=stderr)
        exit(1)
    else:
        proc = run(
            (
                executable,
                "-m",
                "pip",
                "install",
                "--upgrade",
                "--target",
                str(_RT_DIR),
                "--requirement",
                str(REQUIREMENTS),
            ),
            stdin=DEVNULL,
            stderr=stdout,
            cwd=str(_RT_DIR),
        )
        if proc.returncode:
            print("Installation failed, check :message", file=stderr)
            exit(proc.returncode)
        else:
            _DEPS_LOCK.parent.mkdir(parents=True, exist_ok=True)
            _DEPS_LOCK.write_bytes(REQUIREMENTS.read_bytes())
            msg = """
            ---
            This is not an error:
            You can now use :CHADopen
            """
            msg = dedent(msg)
            print(msg, file=stderr)

elif command == "run":
    msg = """
    Please update dependencies using :CHADdeps
    -
    -
    Dependencies will be installed privately inside `chadtree/.vars`
    `rm -rf chadtree/` will cleanly remove everything
    """
    msg = dedent(msg)

    try:
        import pynvim
        import pynvim_pp
        import std2
        import yaml
    except ImportError:
        print(msg, end="", file=stderr)
        exit(1)
    else:
        if (
            not _DEPS_LOCK.exists()
            or _DEPS_LOCK.read_text().strip() != REQUIREMENTS.read_text().strip()
        ):
            print(msg, end="", file=stderr)
            exit(1)
        else:

            from pynvim import attach
            from pynvim_pp.client import run_client

            from .client import ChadClient

            nvim = attach("socket", path=args.socket)
            code = run_client(nvim, client=ChadClient())
            exit(code)

else:
    assert False
