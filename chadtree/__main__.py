from argparse import ArgumentParser, Namespace
from shutil import which
from subprocess import DEVNULL, run
from sys import path, stderr, version_info
from typing import Union

from .consts import REQUIREMENTS, RT_DIR

if version_info < (3, 8, 2):
    msg = "For python < 3.8.2 please install using the branch -- legacy"
    print(msg, end="", file=stderr)


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
command = Union[Literal["deps"], Literal["run"]]

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
            cwd=str(RT_DIR),
        )
        if proc.returncode:
            exit(proc.returncode)

elif command == "run":
    try:
        import pynvim
        import pynvim_pp
        import std2
        import yaml
    except ImportError:
        msg = "Plesae install dependencies locally using :CHADdeps"
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
