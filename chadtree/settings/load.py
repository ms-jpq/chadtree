from dataclasses import dataclass
from enum import Enum, auto
from json import loads
from locale import strxfrm
from typing import (
    AbstractSet,
    Mapping,
    Optional,
    Sequence,
    SupportsFloat,
    Union,
)

from pynvim.api.nvim import Nvim
from pynvim_pp.rpc import RpcSpec
from std2.configparser import hydrate
from std2.pickle import DecodeError, decode
from std2.tree import merge
from std2.types import never
from yaml import safe_load

from ..consts import (
    ASCII_ICONS_JSON,
    CONFIG_YML,
    DEVI_ICONS_JSON,
    EMOJI_ICONS_JSON,
    SETTINGS_VAR,
)
from ..view.parse_colours import load_colours
from ..view.types import ColourChoice, HLGroups, Icons, Sortby
from .types import Ignored, MimetypeOptions, Settings, VersionCtlOpts, ViewOptions


class _OpenDirection(Enum):
    left = auto()
    right = auto()


class _IconSet(Enum):
    ascii = auto()
    emoji = auto()
    devicons = auto()


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
class _UserView:
    open_direction: _OpenDirection
    width: int
    sort_by: Sequence[Sortby]
    icon_set: _IconSet
    colours: ColourChoice
    highlights: HLGroups
    time_format: str
    window_options: Mapping[str, Union[bool, str]]


@dataclass(frozen=True)
class _UserConfig:
    keymap: Mapping[str, AbstractSet[str]]
    options: _UserOptions
    view: _UserView
    ignore: Ignored


def _key_sort(keys: AbstractSet[str]) -> Sequence[str]:
    return sorted((key[len("CHAD") :] for key in keys), key=strxfrm)


def initial(nvim: Nvim, specs: Sequence[RpcSpec]) -> Settings:
    user_config = nvim.vars.get(SETTINGS_VAR, {})

    config: _UserConfig = decode(
        _UserConfig,
        merge(safe_load(CONFIG_YML.read_bytes()), hydrate(user_config), replace=True),
    )
    options, view = config.options, config.view

    if view.icon_set is _IconSet.ascii:
        icons_spec = ASCII_ICONS_JSON
    elif view.icon_set is _IconSet.emoji:
        icons_spec = EMOJI_ICONS_JSON
    elif view.icon_set is _IconSet.devicons:
        icons_spec = DEVI_ICONS_JSON
    else:
        never(view.icon_set)

    icons: Icons = decode(Icons, loads(icons_spec.read_text()))
    hl_context = load_colours(
        nvim,
        colours=view.colours,
        particular_mappings=view.highlights,
    )

    view_opts = ViewOptions(
        hl_context=hl_context,
        icons=icons,
        sort_by=view.sort_by,
        use_icons=view.icon_set is not _IconSet.ascii,
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
