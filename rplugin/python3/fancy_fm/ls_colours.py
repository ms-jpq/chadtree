from dataclasses import dataclass
from enum import Enum, IntEnum, auto
from itertools import chain, repeat
from os import environ
from pprint import pprint
from typing import Callable, Dict, Iterator, Optional, Set, Tuple, Union, cast


class Style(IntEnum):
    bold = 1
    dimmed = 2
    italic = 3
    underline = 4
    blink = 5
    reverse = 7
    hidden = 8
    strikethrough = 9


class Ground(Enum):
    fore = auto()
    back = auto()


class AnsiColour(IntEnum):
    black = 0
    red = 1
    green = 2
    yellow = 3
    blue = 4
    purple = 5
    cyan = 6
    white = 7

    black_bright = 10
    red_bright = 11
    green_bright = 12
    yellow_bright = 13
    blue_bright = 14
    purple_bright = 15
    cyan_bright = 16
    white_bright = 17


@dataclass(frozen=True)
class Colour:
    r: int
    g: int
    b: int


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
        ((c + 30, c) for c in AnsiColour), ((c + 90, c) for c in AnsiColour)
    )
}

RGB_TABLE: Set[str] = {"38", "48"}


def parse_8(codes: Iterator[str]) -> Optional[Colour]:
    try:
        rgb = int(next(codes, ""))
    except ValueError:
        return None
    else:
        if 0 <= rgb <= 255:
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
    for ret in parse_codes(codes):
        if type(ret) is Style:
            styles.add(cast(Style, ret))
        elif type(ret) is tuple:
            ground, colour = cast(Tuple[Ground, Union[AnsiColour, Colour]], ret)


def parse_ls_colours() -> None:
    colours = environ.get("LS_COLORS", "")
    lookup = {
        k: v
        for k, _, v in (
            segment.partition("=") for segment in colours.strip(":").split(":")
        )
    }

    reset = lookup.pop("rs", None)
    normal = lookup.pop("no", None)
    file = lookup.pop("fi", None)
    directory = lookup.pop("di", None)
    link = lookup.pop("ln", None)
    pipe = lookup.pop("pi", None)
    block_device = lookup.pop("bd", None)
    char_device = lookup.pop("cd", None)
    orphan_link = lookup.pop("or", None)
    socket = lookup.pop("so", None)
    executable = lookup.pop("ex", None)
    sticky_dir = lookup.pop("st", None)
    door = lookup.pop("do", None)
    sticky_writable = lookup.pop("tw", None)
    other_writable = lookup.pop("ow", None)
    set_uid = lookup.pop("su", None)
    multi_hardlink = lookup.pop("mh", None)
    file_w_capacity = lookup.pop("ca", None)
    set_gid = lookup.pop("sg", None)

    special = (
        normal,
        file,
        multi_hardlink,
        directory,
        file_w_capacity,
        sticky_writable,
        other_writable,
        link,
        pipe,
        block_device,
        set_gid,
        char_device,
        set_uid,
        orphan_link,
        socket,
        executable,
        sticky_dir,
        door,
        reset,
    )
    exts = tuple(key for key in lookup if key.startswith("*"))
    ext_lookup = {key: lookup.pop(key) for key in exts}
    pprint(ext_lookup)


pprint(STYLE_TABLE)
