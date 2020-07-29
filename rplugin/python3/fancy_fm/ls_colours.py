from dataclasses import dataclass
from enum import Enum, IntEnum, auto
from fnmatch import fnmatch
from itertools import chain, repeat
from os import environ
from typing import Callable, Dict, Iterator, Optional, Set, Tuple, Union, cast

from .highlight import HLgroup
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


@dataclass(frozen=True)
class Styling:
    styles: Set[Style]
    foreground: Union[AnsiColour, Colour, None]
    background: Union[AnsiColour, Colour, None]


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

E_BASIC_TABLE: Dict[int, AnsiColour] = {i: c for i, c in enumerate(AnsiColour)}

E_GREY_TABLE: Dict[int, Colour] = {
    i: Colour(r=s, g=s, b=s)
    for i, s in enumerate((round(step / 23 * 255) for step in range(24)), 232)
}


def parse_8(codes: Iterator[str]) -> Union[AnsiColour, Colour, None]:
    try:
        ansi_code = int(next(codes, ""))
    except ValueError:
        return None
    else:
        if ansi_code in ANSI_RANGE:
            basic = E_BASIC_TABLE.get(ansi_code)
            if basic:
                return basic
            grey = E_GREY_TABLE.get(ansi_code)
            if grey:
                return grey
            ratio = 255 / 5
            code = ansi_code - 16
            r = code // 36
            g = code % 36 // 6
            b = code % 36 % 6
            return Colour(r=round(r * ratio), g=round(g * ratio), b=round(b * ratio))
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


PARSE_TABLE: Dict[str, Callable[[Iterator[str]], Union[AnsiColour, Colour, None]]] = {
    "5": parse_8,
    "2": parse_24,
}


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


HL_STYLE_TABLE: Dict[Style, Optional[str]] = {
    Style.bold: "bold",
    Style.dimmed: None,
    Style.italic: "italic",
    Style.underline: "underline",
    Style.blink: None,
    Style.blink_fast: None,
    Style.reverse: "reverse",
    Style.hidden: None,
    Style.strikethrough: "strikethrough",
}


def parse_codes(
    codes: str,
) -> Iterator[Union[Style, Tuple[Ground, Union[AnsiColour, Colour]]]]:
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


def to_hex(colour: Colour) -> str:
    r, g, b = format(colour.r, "02x"), format(colour.g, "02x"), format(colour.b, "02x")
    return f"#{r}{g}{b}"


def parse_styling(codes: str) -> Styling:
    styles: Set[Style] = set()
    colours: Dict[Ground, Union[AnsiColour, Colour]] = {}
    for ret in parse_codes(codes):
        if type(ret) is Style:
            styles.add(cast(Style, ret))
        elif type(ret) is tuple:
            ground, colour = cast(Tuple[Ground, Union[AnsiColour, Colour]], ret)
            colours[ground] = colour

    styling = Styling(
        styles=styles,
        foreground=colours.get(Ground.fore),
        background=colours.get(Ground.back),
    )
    return styling


def parseHLGroup(name: str, styling: Styling) -> HLgroup:
    fg, bg = styling.foreground, styling.background
    cterm = {
        style
        for style in (HL_STYLE_TABLE.get(style) for style in styling.styles)
        if style
    }
    ctermfg = str(cast(AnsiColour, fg).value) if type(fg) is AnsiColour else None
    ctermbg = str(cast(AnsiColour, bg).value) if type(fg) is AnsiColour else None
    guifg = to_hex(cast(Colour, fg)) if type(fg) is Colour else None
    guibg = to_hex(cast(Colour, bg)) if type(bg) is Colour else None
    group = HLgroup(
        name=name,
        cterm=cterm,
        ctermfg=ctermfg,
        ctermbg=ctermbg,
        guifg=guifg,
        guibg=guibg,
    )
    return group


def parse_ls_colours() -> None:
    colours = environ.get("LS_COLORS", "")
    hl_lookup: Dict[str, HLgroup] = {
        k: parseHLGroup(k, parse_styling(v))
        for k, _, v in (
            segment.partition("=") for segment in colours.strip(":").split(":")
        )
    }

    special_lookup: Dict[Optional[Mode], HLgroup] = {
        k: v
        for k, v in ((v, hl_lookup.pop(k, None)) for k, v in SPECIAL_TABLE.items())
        if v
    }

    fn_keys = tuple(key for key in hl_lookup if key.startswith("*"))
    fn_lookup: Dict[str, HLgroup] = {key: hl_lookup.pop(key) for key in fn_keys}

    def special_search(modes: Set[Mode]) -> Optional[HLgroup]:
        for mode in sorted(modes):
            hl = special_lookup.get(mode)
            if hl:
                return hl
        return special_lookup.get(None)

    def fn_search(filename: str) -> Optional[HLgroup]:
        for pattern, group in fn_lookup.items():
            if fnmatch(filename, pattern):
                return group
        return None
