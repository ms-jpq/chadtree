from argparse import ArgumentParser
from dataclasses import dataclass
from typing import NoReturn, Optional, Sequence

from pynvim import Nvim

from ..registry import rpc
from ..settings.types import Settings
from ..state.types import State
from .types import Stage


@dataclass(frozen=True)
class OpenArgs:
    focus: bool


class _ArgparseError(Exception):
    pass


class _Argparse(ArgumentParser):
    def error(self, message: str) -> NoReturn:
        raise _ArgparseError(message)

    def exit(self, status: int = 0, message: Optional[str] = None) -> NoReturn:
        msg = self.format_help()
        raise _ArgparseError(msg)


def _parse_args(args: Sequence[str]) -> OpenArgs:
    parser = _Argparse()
    parser.add_argument("--nofocus", dest="focus", action="store_false", default=True)

    ns = parser.parse_args(args=args)
    opts = OpenArgs(focus=ns.focus)
    return opts


@rpc(blocking=False, name="CHADopen")
def c_open(
    nvim: Nvim, state: State, settings: Settings, args: Sequence[str]
) -> Optional[Stage]:
    """
    Toggle sidebar
    """

    try:
        opts = _parse_args(args)
    except _ArgparseError as e:
        s_write(nvim, e, error=True)
        return None
    else:
        current = find_current_buffer_name(nvim)
        toggle_fm_window(nvim, state=state, settings=settings, opts=opts)

        stage = _current(nvim, state=state, settings=settings, current=current)
        if stage:
            return stage
        else:
            return Stage(state)
