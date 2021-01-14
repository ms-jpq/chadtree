from dataclasses import dataclass
from locale import strxfrm
from typing import AbstractSet, Literal, Mapping, Optional, Sequence, SupportsFloat, Union

from pynvim.api.nvim import Nvim
from pynvim_pp.rpc import RpcSpec
from std2.pickle import DecodeError, decode
from std2.tree import merge

from ..consts import (
    COLOURS_JSON,
    COLOURS_VAR,
    CONFIG_JSON,
    CUSTOM_COLOURS_JSON,
    ICON_LOOKUP,
    IGNORE_JSON,
    IGNORES_VAR,
    SETTINGS_VAR,
    VIEW_JSON,
    VIEW_VAR,
)
from ..da import load_json
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
        _UserConfig, merge(load_json(CONFIG_JSON), user_config, replace=True)
    )
    view: _UserView = decode(
        _UserView, merge(load_json(VIEW_JSON), user_view, replace=True)
    )
    ignore: UserIgnore = decode(
        UserIgnore, merge(load_json(IGNORE_JSON), user_ignores, replace=True)
    )
    colours: _UserColours = decode(
        _UserColours, merge(load_json(CUSTOM_COLOURS_JSON), user_colours)
    )
    icons: UserIcons = decode(UserIcons, load_json(ICON_LOOKUP[config.use_icons]))
    github_colours: Mapping[str, str] = decode(
        Mapping[str, str], load_json(COLOURS_JSON)
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
    legal_keys = frozenset(name for name, _ in specs)
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
        polling_rate=float(config.polling_rate),
        session=config.session,
        show_hidden=config.show_hidden,
        version_ctl=config.version_control,
        view=view_opts,
        width=config.width,
        win_local_opts=view.window_options,
    )

    return settings
