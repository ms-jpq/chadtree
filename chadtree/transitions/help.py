from enum import Enum, auto
from pathlib import Path
from typing import Sequence, Tuple
from uuid import uuid4
from webbrowser import open as open_w

from pynvim_pp.buffer import Buffer
from pynvim_pp.float_win import list_floatwins, open_float_win
from pynvim_pp.nvim import Nvim
from std2.argparse import ArgparseError, ArgParser
from std2.types import never

from ..consts import (
    CONFIGURATION_MD,
    CONFIGURATION_URI,
    FEATURES_MD,
    FEATURES_URI,
    KEYBIND_MD,
    KEYBIND_URI,
    MIGRATION_MD,
    MIGRATION_URI,
    README_MD,
    README_URI,
    THEME_MD,
    THEME_URI,
)
from ..registry import rpc
from ..settings.types import Settings
from ..state.types import State

_NS = uuid4()


class _Topics(Enum):
    index = auto()
    features = auto()
    keybind = auto()
    config = auto()
    theme = auto()
    migration = auto()


def _directory(topic: _Topics) -> Tuple[Path, str]:
    if topic is _Topics.index:
        return README_MD, README_URI
    elif topic is _Topics.features:
        return FEATURES_MD, FEATURES_URI
    elif topic is _Topics.keybind:
        return KEYBIND_MD, KEYBIND_URI
    elif topic is _Topics.config:
        return CONFIGURATION_MD, CONFIGURATION_URI
    elif topic is _Topics.theme:
        return THEME_MD, THEME_URI
    elif topic is _Topics.migration:
        return MIGRATION_MD, MIGRATION_URI
    else:
        never(topic)


def _parse_args(args: Sequence[str]) -> Tuple[_Topics, bool]:
    parser = ArgParser()
    parser.add_argument(
        "topic",
        nargs="?",
        choices=tuple(topic.name for topic in _Topics),
        default=_Topics.index.name,
    )
    parser.add_argument("-w", "--web", action="store_true", default=False)
    ns = parser.parse_args(args)
    return _Topics[ns.topic], ns.web


@rpc(blocking=False)
async def _help(state: State, settings: Settings, args: Sequence[str]) -> None:
    """
    Open help doc
    """

    try:
        topic, use_web = _parse_args(args)
    except ArgparseError as e:
        await Nvim.write(e, error=True)
    else:
        md, uri = _directory(topic)
        web_d = open_w(uri) if use_web else False
        if not web_d:
            async for win in list_floatwins(_NS):
                await win.close()
            lines = md.read_text("UTF-8").splitlines()
            buf = await Buffer.create(
                listed=False, scratch=True, wipe=True, nofile=True, noswap=True
            )
            await buf.set_lines(lines=lines)
            await buf.opts.set("modifiable", val=False)
            await buf.opts.set("syntax", val="markdown")
            await open_float_win(_NS, margin=0, relsize=0.95, buf=buf, border="rounded")
