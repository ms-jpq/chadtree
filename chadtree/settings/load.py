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
from std2.pickle import DecodeError, decode
from std2.tree import merge
from yaml import safe_load

from ..consts import (
    COLOURS_JSON,
    COLOURS_VAR,
    CONFIG_YML,
    CUSTOM_COLOURS_YML,
    ICON_LOOKUP_JSON,
    IGNORE_YML,
    IGNORES_VAR,
    SETTINGS_VAR,
    VIEW_VAR,
    VIEW_YML,
)
from ..view.highlight import gen_hl
from ..view.ls_colours import parse_ls_colours
from ..view.types import (
    Sortby,
    UserColourMapping,
    UserHighlights,
    UserHLGroups,
    UserIcons,
)
from .types import MimetypeOptions, Settings, UserIgnore, VersionCtlOpts, ViewOptions


@dataclass(frozen=True)
class _UserConfig:
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
class _UserColours:
    eight_bit: Mapping[str, UserColourMapping]


def initial(nvim: Nvim, specs: Sequence[RpcSpec]) -> Settings:
    user_config = nvim.vars.get(SETTINGS_VAR, {})
    user_view = nvim.vars.get(VIEW_VAR, {})
    user_ignores = nvim.vars.get(IGNORES_VAR, {})
    user_colours = nvim.vars.get(COLOURS_VAR, {})

    config: _UserConfig = decode(
        _UserConfig,
        merge(safe_load(CONFIG_YML.read_bytes()), user_config, replace=True),
    )
    view: _UserView = decode(
        _UserView, merge(safe_load(VIEW_YML.read_bytes()), user_view, replace=True)
    )
    ignore: UserIgnore = decode(
        UserIgnore,
        merge(safe_load(IGNORE_YML.read_bytes()), user_ignores, replace=True),
    )
    colours: _UserColours = decode(
        _UserColours, merge(safe_load(CUSTOM_COLOURS_YML.read_bytes()), user_colours)
    )
    icons: UserIcons = decode(
        UserIcons, load(ICON_LOOKUP_JSON[config.use_icons].open())
    )
    github_colours: Mapping[str, str] = decode(
        Mapping[str, str], load(COLOURS_JSON.open())
    )

    ext_colours = gen_hl("github", mapping=github_colours)
    highlights = UserHighlights(
        eight_bit=colours.eight_bit, exts=ext_colours, groups=view.highlights
    )
    hl_context = parse_ls_colours(highlights)

    view_opts = ViewOptions(
        hl_context=hl_context,
        highlights=highlights,
        icons=icons,
        sort_by=config.sort_by,
        use_icons=bool(config.use_icons),
        time_fmt=view.time_format,
    )

    keymap = {f"CHAD{k}": v for k, v in config.keymap.items()}
    legal_keys = {name for name, _ in specs}
    extra_keys = keymap.keys() - legal_keys
    if extra_keys:
        raise DecodeError(
            path=(_UserConfig, "<field 'keymap'>"),
            actual=None,
            missing_keys=(),
            extra_keys=sorted((key[len("CHAD") :] for key in extra_keys), key=strxfrm),
        )

    settings = Settings(
        follow=config.follow,
        ignores=ignore,
        keymap=keymap,
        lang=config.lang,
        mime=config.mimetypes,
        open_left=config.open_left,
        page_increment=config.page_increment,
        polling_rate=float(config.polling_rate),
        session=config.session,
        show_hidden=config.show_hidden,
        version_ctl=config.version_control,
        view=view_opts,
        width=config.width,
        win_local_opts=view.window_options,
    )

    return settings
