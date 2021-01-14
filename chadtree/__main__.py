from sys import stderr, version_info

if version_info < (3, 8, 2):
    msg = "For python < 3.8.2 please install using the branch -- legacy"
    print(msg, end="", file=stderr)
    exit(1)

try:
    import pynvim
except ImportError:
    msg = "Plesae install pynvim"
    print(msg, end="", file=stderr)
    exit(1)


try:
    import pynvim_pp
    import std2
except ImportError:
    msg = "Plesae install pynvim"
    print(msg, file=stderr)
    exit(1)

from argparse import ArgumentParser, Namespace


def parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("socket")
    return parser.parse_args()


from pynvim import attach
from pynvim_pp.client import run_client

from .client import ChadClient


def main() -> None:
    args = parse_args()
    nvim = attach("socket", path=args.socket)
    code = run_client(nvim, client=ChadClient())
    exit(code)


main()
