from argparse import ArgumentParser
from typing import NoReturn

from .types import OpenArgs, Sequence


class ArgparseError(Exception):
    pass


class Argparse(ArgumentParser):
    def error(self, message: str) -> NoReturn:
        raise ArgparseError(message)

    def exit(self, status: int = 0, message: str = "") -> NoReturn:
        msg = self.format_help()
        raise ArgparseError(msg)


def parse_args(args: Sequence[str]) -> OpenArgs:
    parser = Argparse()
    parser.add_argument("--nofocus", dest="focus", action="store_false")

    ns = parser.parse_args(args=args)
    opts = OpenArgs(focus=ns.focus)
    return opts
