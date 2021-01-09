from argparse import ArgumentParser
from dataclasses import dataclass
from typing import NoReturn, Optional, Sequence


@dataclass(frozen=True)
class _OpenArgs:
    focus: bool

class _ArgparseError(Exception):
    pass


class _Argparse(ArgumentParser):
    def error(self, message: str) -> NoReturn:
        raise _ArgparseError(message)

    def exit(self, status: int = 0, message: Optional[str] = None) -> NoReturn:
        msg = self.format_help()
        raise _ArgparseError(msg)


def _parse_args(args: Sequence[str]) -> _OpenArgs:
    parser = _Argparse()
    parser.add_argument("--nofocus", dest="focus", action="store_false", default=True)

    ns = parser.parse_args(args=args)
    opts = _OpenArgs(focus=ns.focus)
    return opts
