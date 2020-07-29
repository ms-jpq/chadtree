from dataclasses import dataclass
from enum import Enum, IntEnum, auto
from itertools import chain, repeat
from os import environ
from typing import Callable, Dict, Iterator, Optional, Set, Tuple, Union, cast

from .types import Mode


class Style(IntEnum):
    bold = auto()
    dimmed = auto()
    italic = auto()
    underline = auto()
    blink = auto()
    blink_fast = auto()
    reverse = auto()
    hidden = auto()
    strikethrough = auto()


class Ground(Enum):
    fore = auto()
    back = auto()


class AnsiColour(IntEnum):
    black = auto()
    red = auto()
    green = auto()
    yellow = auto()
    blue = auto()
    purple = auto()
    cyan = auto()
    white = auto()

    black_bright = auto()
    red_bright = auto()
    green_bright = auto()
    yellow_bright = auto()
    blue_bright = auto()
    purple_bright = auto()
    cyan_bright = auto()
    white_bright = auto()


@dataclass(frozen=True)
class Colour:
    r: int
    g: int
    b: int


SPECIAL_TABLE: Dict[str, Optional[Mode]] = {
    "bd": Mode.block_device,
    "cd": Mode.char_device,
    "do": Mode.door,
    "ex": Mode.executable,
    "fi": Mode.file,
    "ca": Mode.file_w_capacity,
    "di": Mode.folder,
    "ln": Mode.link,
    "mh": Mode.multi_hardlink,
    "no": None,
    "or": Mode.orphan_link,
    "ow": Mode.other_writable,
    "pi": Mode.pipe,
    "so": Mode.socket,
    "st": Mode.sticky_dir,
    "tw": Mode.sticky_writable,
    "sg": Mode.set_gid,
    "su": Mode.set_uid,
}


ANSI_RANGE = range(256)
RGB_RANGE = range(256)

STYLE_TABLE: Dict[str, Style] = {str(code + 0): code for code in Style}

GROUND_TABLE: Dict[str, Ground] = {
    str(code): ground
    for code, ground in chain(
        zip(chain(range(30, 39), range(90, 98)), repeat(Ground.fore)),
        zip(chain(range(40, 49), range(100, 108)), repeat(Ground.back)),
    )
}

COLOUR_TABLE: Dict[str, AnsiColour] = {
    str(code): colour
    for code, colour in chain(
        ((c + 29 if c <= 8 else c + 31, c) for c in AnsiColour),
        ((c + 89 if c <= 8 else c + 91, c) for c in AnsiColour),
    )
}

RGB_TABLE: Set[str] = {"38", "48"}


def to_hex(colour: Colour) -> str:
    r, g, b = format(colour.r, "02x"), format(colour.g, "02x"), format(colour.b, "02x")
    return f"#{r}{g}{b}"


def parse_8(codes: Iterator[str]) -> Optional[Colour]:
    try:
        ansi_code = int(next(codes, ""))
    except ValueError:
        return None
    else:
        if ansi_code in ANSI_RANGE:
            return Colour(r=0, g=0, b=0)
        else:
            return None


def parse_24(codes: Iterator[str]) -> Optional[Colour]:
    try:
        r, g, b = int(next(codes, "")), int(next(codes, "")), int(next(codes, ""))
    except ValueError:
        return None
    else:
        if r in RGB_RANGE and g in RGB_RANGE and b in RGB_RANGE:
            return Colour(r=r, g=g, b=b)
        else:
            return None


PARSE_TABLE: Dict[str, Callable[[Iterator[str]], Optional[Colour]]] = {
    "2": parse_8,
    "5": parse_24,
}


def parse_codes(
    codes: str,
) -> Iterator[Union[Style, Tuple[Ground, AnsiColour], Tuple[Ground, Colour]]]:
    it = (code.lstrip("0") for code in codes.split(";"))
    for code in it:
        style = STYLE_TABLE.get(code)
        if style:
            yield style
            continue
        ground = GROUND_TABLE.get(code)
        ansi_colour = COLOUR_TABLE.get(code)
        if ground and ansi_colour:
            yield ground, ansi_colour
        elif ground and code in RGB_TABLE:
            code = next(it, "")
            parse = PARSE_TABLE.get(code)
            if parse:
                colour = parse(it)
                if colour:
                    yield ground, colour


def parse_fuck(codes: str) -> None:
    styles: Set[Style] = set()
    colours: Dict[Ground, Union[AnsiColour, Colour]] = {}
    for ret in parse_codes(codes):
        if type(ret) is Style:
            styles.add(cast(Style, ret))
        elif type(ret) is tuple:
            ground, colour = cast(Tuple[Ground, Union[AnsiColour, Colour]], ret)
            colours[ground] = colour


def parse_ls_colours() -> None:
    colours = environ.get("LS_COLORS", "")
    lookup = {
        k: v
        for k, _, v in (
            segment.partition("=") for segment in colours.strip(":").split(":")
        )
    }

    exts = tuple(key for key in lookup if key.startswith("*"))
    ext_lookup = {key: lookup.pop(key) for key in exts}
