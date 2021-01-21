from dataclasses import dataclass
from enum import Enum, auto
from locale import strxfrm
from typing import AbstractSet, Mapping, Optional, Sequence, SupportsFloat, Union

from chad_types import (
    ARTIFACT,
    Artifact,
    IconColourSetEnum,
    IconGlyphSetEnum,
    LSColoursEnum,
    TextColourSetEnum,
)
from pynvim.api.nvim import Nvim
from pynvim_pp.rpc import RpcSpec
from std2.configparser import hydrate
from std2.pickle import DecodeError, decode
from std2.tree import merge
from yaml import safe_load

from ..consts import CONFIG_YML, SETTINGS_VAR
from ..view.load import load_theme
from ..view.types import HLGroups, Sortby
from .types import Ignored, MimetypeOptions, Settings, VersionCtlOpts, ViewOptions


class _OpenDirection(Enum):
    left = auto()
    right = auto()


@dataclass(frozen=True)
class _UserOptions:
    follow: bool
    lang: Optional[str]
    mimetypes: MimetypeOptions
    page_increment: int
    polling_rate: SupportsFloat
    session: bool
    show_hidden: bool
    version_control: VersionCtlOpts


@dataclass(frozen=True)
class _UserTheme:
    highlights: HLGroups
    icon_glyph_set: IconGlyphSetEnum
    icon_colour_set: IconColourSetEnum
    text_colour_set: Union[LSColoursEnum, TextColourSetEnum]
    discrete_colour_map: Mapping[str, str]

@dataclass(frozen=True)
class _UserView:
    open_direction: _OpenDirection
    width: int
    sort_by: Sequence[Sortby]
    time_format: str
    window_options: Mapping[str, Union[bool, str]]


@dataclass(frozen=True)
class _UserConfig:
    keymap: Mapping[str, AbstractSet[str]]
    options: _UserOptions
    ignore: Ignored
    view: _UserView
    theme: _UserTheme


def _key_sort(keys: AbstractSet[str]) -> Sequence[str]:
    return sorted((key[len("CHAD") :] for key in keys), key=strxfrm)


def initial(nvim: Nvim, specs: Sequence[RpcSpec]) -> Settings:
    artifacts: Artifact = decode(Artifact, safe_load(ARTIFACT.read_bytes()))

    user_config = nvim.vars.get(SETTINGS_VAR, {})
    config: _UserConfig = decode(
        _UserConfig,
        merge(safe_load(CONFIG_YML.read_bytes()), hydrate(user_config), replace=True),
    )
    options, view, theme = config.options, config.view, config.theme

    icons, hl_context = load_theme(
        nvim,
        artifact=artifacts,
        particular_mappings=theme.highlights,
        discrete_colours=theme.discrete_colour_map,
        icon_set=theme.icon_glyph_set,
        icon_colour_set=theme.icon_colour_set,
        text_colour_set=theme.text_colour_set,
    )

    view_opts = ViewOptions(
        hl_context=hl_context,
        icons=icons,
        sort_by=view.sort_by,
        use_icons=theme.icon_glyph_set is not IconGlyphSetEnum.ascii,
        time_fmt=view.time_format,
    )

    keymap = {f"CHAD{k}": v for k, v in config.keymap.items()}
    legal_keys = {name for name, _ in specs}
    extra_keys = keymap.keys() - legal_keys

    if extra_keys:
        raise DecodeError(
            path=(_UserOptions, _key_sort(legal_keys)),
            actual=None,
            missing_keys=(),
            extra_keys=_key_sort(extra_keys),
        )

    settings = Settings(
        follow=options.follow,
        ignores=config.ignore,
        keymap=keymap,
        lang=options.lang,
        mime=options.mimetypes,
        open_left=view.open_direction is _OpenDirection.left,
        page_increment=options.page_increment,
        polling_rate=float(options.polling_rate),
        session=options.session,
        show_hidden=options.show_hidden,
        version_ctl=options.version_control,
        view=view_opts,
        width=view.width,
        win_local_opts=view.window_options,
    )

    return settings
