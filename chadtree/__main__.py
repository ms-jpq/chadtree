from argparse import ArgumentParser, Namespace
from os import name
from pathlib import Path
from subprocess import DEVNULL, run
from sys import executable, stderr, stdout, version_info
from textwrap import dedent
from webbrowser import open as open_w

from .consts import MIGRATION_URI, REQUIREMENTS, RT_DIR, RT_DIR_XDG, RT_PY, RT_PY_XDG

if version_info < (3, 8, 2):
    msg = "For python < 3.8.2 please install using the branch -- legacy"
    print(msg, end="", file=stderr)
    open_w(MIGRATION_URI)
    exit(1)


def parse_args() -> Namespace:
    parser = ArgumentParser()
    sub_parsers = parser.add_subparsers(dest="command", required=True)

    s_run = sub_parsers.add_parser("run")
    s_run.add_argument("--socket", required=True)
    s_run.add_argument("--xdg", action="store_true")

    s_deps = sub_parsers.add_parser("deps")
    s_deps.add_argument("--xdg", action="store_true")

    return parser.parse_args()


is_win = name == "nt"
args = parse_args()
py3 = Path(args.python) if args.python else None
command: str = args.command

use_xdg = False if is_win else args.xdg
_RT_DIR = RT_DIR_XDG if use_xdg else RT_DIR
_RT_PY = RT_PY_XDG if use_xdg else RT_PY

if command == "deps":
    try:
        from venv import EnvBuilder

        print("...", flush=True)
        if is_win and _RT_DIR.exists():
            pass
        else:
            EnvBuilder(
                system_site_packages=False,
                with_pip=True,
                upgrade=True,
                symlinks=not is_win,
                clear=True,
            ).create(_RT_DIR)
    except (ImportError, SystemExit):
        print("Please install venv separately.", file=stderr)
        exit(1)
    else:
        proc = run(
            (
                py3 or _RT_PY,
                "-m",
                "pip",
                "install",
                "--upgrade",
                "--requirement",
                str(REQUIREMENTS),
            ),
            stdin=DEVNULL,
            stderr=stdout,
        )
        if proc.returncode:
            print("Installation failed, check :message", file=stderr)
            exit(proc.returncode)
        else:
            msg = """
            ---
            This is not an error:
            You can now use :CHADopen
            """
            msg = dedent(msg)
            print(msg, file=stderr)

elif command == "run":
    try:
        if executable != _RT_PY:
            raise RuntimeError()
        else:
            import pynvim
            import pynvim_pp
            import std2
            import yaml
    except (ImportError, RuntimeError):
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
        from pynvim import attach
        from pynvim_pp.client import run_client

        from .client import ChadClient

        nvim = attach("socket", path=args.socket)
        code = run_client(nvim, client=ChadClient())
        exit(code)

else:
    assert False
