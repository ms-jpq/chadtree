from dataclasses import dataclass
from json import loads
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
    CONFIG_YML,
    GITHUB_COLOURS_JSON,
    ICON_LOOKUP_JSON,
    NERD_COLOURS_JSON,
    SETTINGS_VAR,
)
from ..view.parse_colours import parse_colours
from ..view.types import (
    ColourChoice,
    GithubColours,
    NerdColours,
    Sortby,
    UserHLGroups,
    UserIcons,
)
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
    colours: ColourChoice
    highlights: UserHLGroups
    time_format: str
    window_options: Mapping[str, Union[bool, str]]


@dataclass(frozen=True)
class _UserConfig:
    view: _UserView
    options: _UserOptions
    ignore: UserIgnore


def _key_sort(keys: AbstractSet[str]) -> Sequence[str]:
    return sorted((key[len("CHAD") :] for key in keys), key=strxfrm)


def initial(nvim: Nvim, specs: Sequence[RpcSpec]) -> Settings:
    user_config = nvim.vars.get(SETTINGS_VAR, {})
    light_theme = nvim.options["background"] == "light"

    config: _UserConfig = decode(
        _UserConfig,
        merge(safe_load(CONFIG_YML.read_bytes()), user_config, replace=True),
    )
    options, view = config.options, config.view

    icons: UserIcons = decode(
        UserIcons, loads(ICON_LOOKUP_JSON[options.use_icons].read_text())
    )

    github_colours: GithubColours = decode(
        GithubColours, loads(GITHUB_COLOURS_JSON.read_text())
    )
    nerd_colours: NerdColours = decode(
        NerdColours, merge(loads(NERD_COLOURS_JSON.read_text()))
    )

    hl_context = parse_colours(
        colours=view.colours,
        light_theme=light_theme,
        particular_mappings=view.highlights,
        github_colours=github_colours,
        nerd_colours=nerd_colours,
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
        ignores=config.ignore,
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
