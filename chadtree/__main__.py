from argparse import ArgumentParser, Namespace
from shutil import which
from subprocess import DEVNULL, run
from sys import path, stderr, stdout, version_info
from textwrap import dedent
from typing import Union
from webbrowser import open as open_w

from .consts import MIGRATION_URI, REQUIREMENTS, RT_DIR

if version_info < (3, 8, 2):
    msg = "For python < 3.8.2 please install using the branch -- legacy"
    print(msg, end="", file=stderr)
    open_w(MIGRATION_URI)


from importlib.metadata import version
from typing import Literal

RT_DIR.mkdir(parents=True, exist_ok=True)
path.append(str(RT_DIR))


def parse_args() -> Namespace:
    parser = ArgumentParser()

    sub_parsers = parser.add_subparsers(dest="command", required=True)

    s_run = sub_parsers.add_parser("run")
    s_run.add_argument("--socket", required=True)

    s_deps = sub_parsers.add_parser("deps")

    return parser.parse_args()


args = parse_args()
command: Union[Literal["deps"], Literal["run"]] = args.command

if command == "deps":
    cmd = "pip3"
    if not which(cmd):
        print("Cannot find pip3! Please install pip3 separately", file=stderr)
        exit(1)
    else:
        proc = run(
            (
                cmd,
                "install",
                "--upgrade",
                "--target",
                str(RT_DIR),
                "--requirement",
                REQUIREMENTS,
            ),
            stdin=DEVNULL,
            stderr=stdout,
            cwd=str(RT_DIR),
        )
        if proc.returncode:
            print("Installation failed, check :message", file=stderr)
            exit(proc.returncode)
        else:
            print("You can now use :CHADopen", file=stderr)

elif command == "run":
    msg = """
    Please update dependencies using :CHADdeps
    -
    -
    Dependencies will be installed privately inside `chadtree/.vars`
    `rm -rf chadtree/` will cleanly remove everything
    """

    try:
        versions = {
            "std2": "0.1.0",
            "pynvim_pp": "0.1.10",
        }
        import pynvim
        import pynvim_pp
        import std2
        import yaml
    except ImportError:
        print(dedent(msg), end="", file=stderr)
        exit(1)

    else:
        if any(version(lhs) != rhs for lhs, rhs in versions.items()):
            print(dedent(msg), end="", file=stderr)
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
