from dataclasses import dataclass
from enum import Enum, IntEnum, auto
from itertools import chain, repeat
from os import environ
from typing import Callable, Dict, Iterator, Optional, Set, Tuple, Union, cast
from uuid import uuid4

from .consts import fm_hl_prefix
from .types import Colours, HLcontext, HLgroup, Mode


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
    Black = auto()
    Red = auto()
    Green = auto()
    Yellow = auto()
    Blue = auto()
    Magenta = auto()
    Cyan = auto()
    White = auto()

    BrightBlack = auto()
    BrightRed = auto()
    BrightGreen = auto()
    BrightYellow = auto()
    BrightBlue = auto()
    BrightMagenta = auto()
    BrightCyan = auto()
    BrightWhite = auto()


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


SPECIAL_PRE_TABLE: Dict[str, Mode] = {
    "bd": Mode.block_device,
    "cd": Mode.char_device,
    "do": Mode.door,
    "ex": Mode.executable,
    "ca": Mode.file_w_capacity,
    "di": Mode.folder,
    "ln": Mode.link,
    "mh": Mode.multi_hardlink,
    "or": Mode.orphan_link,
    "ow": Mode.other_writable,
    "pi": Mode.pipe,
    "so": Mode.socket,
    "st": Mode.sticky_dir,
    "tw": Mode.sticky_writable,
    "sg": Mode.set_gid,
    "su": Mode.set_uid,
}


SPECIAL_POST_TABLE: Dict[str, Optional[Mode]] = {
    "fi": Mode.file,
    "no": None,
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


def parseHLGroup(styling: Styling, colours: Colours) -> HLgroup:
    bit8_mapping = colours.bit8_mapping
    fg, bg = styling.foreground, styling.background
    name = f"{fm_hl_prefix}_ls_{uuid4().hex}"
    cterm = {
        style
        for style in (HL_STYLE_TABLE.get(style) for style in styling.styles)
        if style
    }
    ansifg = bit8_mapping[cast(AnsiColour, fg).name] if type(fg) is AnsiColour else None
    ansibg = bit8_mapping[cast(AnsiColour, bg).name] if type(bg) is AnsiColour else None
    ctermfg = ansifg.hl8 if ansifg else None
    ctermbg = ansibg.hl8 if ansibg else None
    guifg = (
        to_hex(cast(Colour, fg))
        if type(fg) is Colour
        else (ansifg.hl24 if ansifg else None)
    )
    guibg = (
        to_hex(cast(Colour, bg))
        if type(bg) is Colour
        else (ansibg.hl24 if ansibg else None)
    )
    group = HLgroup(
        name=name,
        cterm=cterm,
        ctermfg=ctermfg,
        ctermbg=ctermbg,
        guifg=guifg,
        guibg=guibg,
    )
    return group


def parse_ls_colours(colours: Colours) -> HLcontext:
    ls_colours = environ.get("LS_COLORS", "")
    hl_lookup: Dict[str, HLgroup] = {
        k: parseHLGroup(parse_styling(v), colours=colours)
        for k, _, v in (
            segment.partition("=") for segment in ls_colours.strip(":").split(":")
        )
    }
    groups = tuple(hl_lookup.values())

    mode_lookup_pre: Dict[Mode, HLgroup] = {
        k: v
        for k, v in ((v, hl_lookup.pop(k, None)) for k, v in SPECIAL_PRE_TABLE.items())
        if v
    }

    mode_lookup_post: Dict[Optional[Mode], HLgroup] = {
        k: v
        for k, v in ((v, hl_lookup.pop(k, None)) for k, v in SPECIAL_POST_TABLE.items())
        if v
    }

    ext_keys = tuple(
        key for key in hl_lookup if key.startswith("*.") and key.count(".") == 1
    )
    ext_lookup: Dict[str, HLgroup] = {key[1:]: hl_lookup.pop(key) for key in ext_keys}

    context = HLcontext(
        groups=groups,
        mode_lookup_pre=mode_lookup_pre,
        mode_lookup_post=mode_lookup_post,
        ext_lookup=ext_lookup,
        name_lookup=hl_lookup,
    )
    return context
