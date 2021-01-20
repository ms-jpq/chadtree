from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Mapping

TOP_LEVEL = Path(__file__).resolve().parent
ASSETS = TOP_LEVEL / "assets"
ARTIFACT = TOP_LEVEL / "artifacts" / "artifact.json"


"""
Icons
"""


Icon = str


@dataclass(frozen=True)
class _FolderIcons:
    open: Icon
    closed: Icon


@dataclass(frozen=True)
class _LinkIcons:
    normal: Icon
    broken: Icon


@dataclass(frozen=True)
class _StatusIcons:
    active: Icon
    inactive: Icon
    selected: Icon
    not_selected: Icon


@dataclass(frozen=True)
class IconGlyphs:
    default_icon: Icon
    folder: _FolderIcons
    link: _LinkIcons
    status: _StatusIcons

    ext_exact: Mapping[str, Icon]
    name_exact: Mapping[str, Icon]
    name_glob: Mapping[str, Icon]


@dataclass(frozen=True)
class IconGlyphSet:
    ascii: IconGlyphs
    devicons: IconGlyphs
    emoji: IconGlyphs


class IconGlyphSetEnum(Enum):
    ascii = auto()
    devicons = auto()
    emoji = auto()


"""
Icon Colours
"""


Hex = str
IconColours = Mapping[str, Hex]


@dataclass(frozen=True)
class IconColourSet:
    github: IconColours


class IconColourSetEnum(Enum):
    github = auto()


"""
Text Colours
"""


@dataclass(frozen=True)
class TextColours:
    ext_exact: Mapping[str, Hex]
    name_exact: Mapping[str, Hex]
    name_glob: Mapping[str, Hex]


@dataclass(frozen=True)
class TextColourSet:
    nerdtree_syntax_light: TextColours
    nerdtree_syntax_dark: TextColours


class TextColourSetEnum(Enum):
    nerdtree_syntax_light = auto()
    nerdtree_syntax_dark = auto()


"""
LS Colours
"""


LS_COLOR = str


@dataclass(frozen=True)
class LSColourSet:
    dark_256: LS_COLOR
    ansi_dark: LS_COLOR
    ansi_light: LS_COLOR
    ansi_universal: LS_COLOR


class LSColoursEnum(Enum):
    none = auto()
    env = auto()
    dark_256 = auto()
    ansi_dark = auto()
    ansi_light = auto()
    ansi_universal = auto()


"""
Artifact
"""


@dataclass(frozen=True)
class Artifact:
    icons: IconGlyphSet
    ls_colours: LSColourSet
    icon_colours: IconColourSet
    text_colours: TextColourSet
