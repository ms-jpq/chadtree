from dataclasses import dataclass
from json import load
from locale import strxfrm
from typing import (
    AbstractSet,
    Literal,
    Mapping,
    Optional,
    Sequence,
    SupportsFloat,
    Union,
)

from pynvim.api.nvim import Nvim
from pynvim_pp.rpc import RpcSpec
from std2.pickle import DecodeError, decode, encode
from std2.tree import merge
from yaml import safe_load

from ..consts import (
    COLOURS_JSON,
    COLOURS_VAR,
    CONFIG_YML,
    CUSTOM_COLOURS_YML,
    ICON_LOOKUP_JSON,
    IGNORES_VAR,
    SETTINGS_VAR,
    VIEW_VAR,
)
from ..view.highlight import gen_hl
from ..view.ls_colours import parse_ls_colours
from ..view.types import Sortby, UserColourMapping, UserHLGroups, UserIcons
from .types import MimetypeOptions, Settings, UserIgnore, VersionCtlOpts, ViewOptions


@dataclass(frozen=True)
class _UserOptions:
    follow: bool
    keymap: Mapping[str, AbstractSet[str]]
    lang: Optional[str]
    mimetypes: MimetypeOptions
    open_left: bool
    page_increment: int
    polling_rate: SupportsFloat
    session: bool
    show_hidden: bool
    sort_by: Sequence[Sortby]
    use_icons: Union[bool, Literal["emoji"]]
    version_control: VersionCtlOpts
    width: int


@dataclass(frozen=True)
class _UserView:
    highlights: UserHLGroups
    time_format: str
    window_options: Mapping[str, Union[bool, str]]


@dataclass(frozen=True)
class _UserConfig:
    view: _UserView
    options: _UserOptions
    ignore: UserIgnore


@dataclass(frozen=True)
class _UserColours:
    eight_bit: Mapping[str, UserColourMapping]


def _key_sort(keys: AbstractSet[str]) -> Sequence[str]:
    return sorted((key[len("CHAD") :] for key in keys), key=strxfrm)


def initial(nvim: Nvim, specs: Sequence[RpcSpec]) -> Settings:
    user_config = nvim.vars.get(SETTINGS_VAR, {})
    user_view = nvim.vars.get(VIEW_VAR, {})
    user_ignores = nvim.vars.get(IGNORES_VAR, {})
    user_colours = nvim.vars.get(COLOURS_VAR, {})

    config: _UserConfig = decode(_UserConfig, safe_load(CONFIG_YML.read_bytes()))

    options: _UserOptions = decode(
        _UserOptions,
        merge(encode(config.options), user_config, replace=True),
    )
    view: _UserView = decode(
        _UserView, merge(encode(config.view), user_view, replace=True)
    )
    ignore: UserIgnore = decode(
        UserIgnore,
        merge(encode(config.ignore), user_ignores, replace=True),
    )
    colours: _UserColours = decode(
        _UserColours, merge(safe_load(CUSTOM_COLOURS_YML.read_bytes()), user_colours)
    )
    icons: UserIcons = decode(
        UserIcons, load(ICON_LOOKUP_JSON[options.use_icons].open())
    )
    github_colours: Mapping[str, str] = decode(
        Mapping[str, str], load(COLOURS_JSON.open())
    )

    github_exts = gen_hl("github", mapping=github_colours)
    hl_context = parse_ls_colours(
        bit8_mapping=colours.eight_bit,
        particular_mappings=view.highlights,
        github_exts=github_exts,
    )

    view_opts = ViewOptions(
        hl_context=hl_context,
        icons=icons,
        sort_by=options.sort_by,
        use_icons=bool(options.use_icons),
        time_fmt=view.time_format,
    )

    keymap = {f"CHAD{k}": v for k, v in options.keymap.items()}
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
        ignores=ignore,
        keymap=keymap,
        lang=options.lang,
        mime=options.mimetypes,
        open_left=options.open_left,
        page_increment=options.page_increment,
        polling_rate=float(options.polling_rate),
        session=options.session,
        show_hidden=options.show_hidden,
        version_ctl=options.version_control,
        view=view_opts,
        width=options.width,
        win_local_opts=view.window_options,
    )

    return settings
