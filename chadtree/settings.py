from dataclasses import dataclass
from locale import strxfrm
from typing import FrozenSet, Literal, Mapping, Optional, Sequence, Union

from pynvim.api.nvim import Nvim
from pynvim_pp.rpc import RpcSpec
from std2.pickle import DecodeError, decode
from std2.tree import merge

from .consts import (
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
from .da import load_json
from .highlight import gen_hl
from .ls_colours import parse_ls_colours
from .registry import rpc
from .types import (
    MimetypeOptions,
    Settings,
    Sortby,
    UserColourMapping,
    UserHighlights,
    UserHLGroups,
    UserIcons,
    UserIgnore,
    VersionCtlOpts,
    ViewOptions,
)


@dataclass(frozen=True)
class UserConfig:
    follow: bool
    keymap: Mapping[str, FrozenSet[str]]
    lang: Optional[str]
    mimetypes: MimetypeOptions
    open_left: bool
    session: bool
    show_hidden: bool
    sort_by: Sequence[Sortby]
    use_icons: Union[bool, Literal["emoji"]]
    version_control: VersionCtlOpts
    width: int


@dataclass(frozen=True)
class UserView:
    highlights: UserHLGroups
    time_format: str
    window_options: Mapping[str, Union[bool, str]]


@dataclass(frozen=True)
class UserColours:
    eight_bit: Mapping[str, UserColourMapping]


def initial(nvim: Nvim, specs: Sequence[RpcSpec]) -> Settings:
    user_config = nvim.vars.get(SETTINGS_VAR, {})
    user_view = nvim.vars.get(VIEW_VAR, {})
    user_ignores = nvim.vars.get(IGNORES_VAR, {})
    user_colours = nvim.vars.get(COLOURS_VAR, {})

    config: UserConfig = decode(
        UserConfig, merge(load_json(CONFIG_JSON), user_config, replace=True)
    )
    view: UserView = decode(
        UserView, merge(load_json(VIEW_JSON), user_view, replace=True)
    )
    ignore: UserIgnore = decode(
        UserIgnore, merge(load_json(IGNORE_JSON), user_ignores, replace=True)
    )
    colours: UserColours = decode(
        UserColours, merge(load_json(CUSTOM_COLOURS_JSON), user_colours)
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
            path=(UserConfig, "<field 'keymap'>"),
            actual=None,
            missing_keys=(),
            extra_keys=sorted(extra_keys, key=strxfrm),
        )

    settings = Settings(
        follow=config.follow,
        ignores=ignore,
        keymap=keymap,
        lang=config.lang,
        mime=config.mimetypes,
        open_left=config.open_left,
        session=config.session,
        show_hidden=config.show_hidden,
        version_ctl=config.version_control,
        view=view_opts,
        width=config.width,
        win_local_opts=view.window_options,
    )

    return settings
