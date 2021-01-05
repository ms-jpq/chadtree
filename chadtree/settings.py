from dataclasses import dataclass
from typing import Any, FrozenSet, Literal, Mapping, Optional, Sequence, Union, cast

from pynvim.api.nvim import Nvim
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
from .types import (
    ColourMapping,
    Colours,
    MimetypeOptions,
    Settings,
    Sortby,
    UpdateTime,
    VersionControlOptions,
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
    version_control: VersionControlOptions
    width: int


@dataclass(frozen=True)
class UserHLOpt:
    quickfix: str
    version_control: str


@dataclass(frozen=True)
class UserView:
    highlights: UserHLOpt
    time_format: str
    window_options: Mapping[str, Union[bool, str]]


@dataclass(frozen=True)
class UserIgnore:
    name: FrozenSet[str]
    path: FrozenSet[str]


@dataclass(frozen=True)
class UserColours:
    eight_bit: Mapping[str, ColourMapping]



def initial(
    nvim: Nvim,
) -> Settings:
    user_config = nvim.vars.get(SETTINGS_VAR, {})
    user_view = nvim.vars.get(VIEW_VAR, {})
    user_ignores = nvim.vars.get(IGNORES_VAR, {})
    user_colours = nvim.vars.get(COLOURS_VAR, {})

    config = merge(load_json(CONFIG_JSON), user_config, replace=True)
    view = merge(load_json(VIEW_JSON), user_view, replace=True)
    icons_json = ICON_LOOKUP[config["use_icons"]]
    icon_c = cast(Any, load_json(icons_json))
    ignore = merge(load_json(IGNORE_JSON), user_ignores, replace=True)
    github_colours = cast(Mapping[str, str], load_json(COLOURS_JSON))
    colours_c = merge(cast(Any, load_json(CUSTOM_COLOURS_JSON)), user_colours)

    use_icons = config["use_icons"]

    bit8_mapping = {
        key: ColourMapping(hl8=val["hl8"], hl24=val["hl24"])
        for key, val in colours_c["8_bit"].items()
    }
    ext_colours = gen_hl("github", mapping=github_colours)
    colours = Colours(bit8_mapping=bit8_mapping, exts=ext_colours)
    icons = ViewOptions(
        active=icon_c["status"]["active"],
        default_icon=icon_c["default_icon"],
        colours=colours,
        filename_exact=icon_c["name_exact"],
        filename_glob=icon_c["name_glob"],
        filetype=icon_c["type"],
        folder_closed=icon_c["folder"]["closed"],
        folder_open=icon_c["folder"]["open"],
        link=icon_c["link"]["normal"],
        link_broken=icon_c["link"]["broken"],
        quickfix_hl=view["highlights"]["quickfix"],
        selected=icon_c["status"]["selected"],
        time_fmt=view["time_format"],
        version_ctl_hl=view["highlights"]["version_control"],
    )

    update = UpdateTime(
        min_time=config["update_time"]["min"], max_time=config["update_time"]["max"]
    )

    version_ctl = VersionControlOptions(
        defer=config["version_control"]["defer"],
        enable=config["version_control"]["enable"],
    )
    hl_context = parse_ls_colours(colours)

    keymap = {f"CHAD{k}": v for k, v in config["keymap"].items()}
    mime = MimetypeOptions(
        warn={*config["mimetypes"]["warn"]},
        ignore_exts={*config["mimetypes"]["ignore_exts"]},
    )

    sortby = tuple(Sortby[sb] for sb in config["sort_by"])
    settings = Settings(
        follow=config["follow"],
        hl_context=hl_context,
        view=icons,
        keymap=keymap,
        lang=config["lang"],
        mime=mime,
        name_ignore=ignore["name"],
        open_left=config["open_left"],
        path_ignore=ignore["path"],
        session=config["session"],
        show_hidden=config["show_hidden"],
        sort_by=sortby,
        update=update,
        use_icons=use_icons,
        version_ctl=version_ctl,
        width=config["width"],
        win_local_opts=view["window_options"],
    )

    return settings
