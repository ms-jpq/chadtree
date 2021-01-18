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
from std2.configparser import hydrate
from std2.pickle import DecodeError, decode
from std2.tree import merge
from yaml import safe_load

from ..consts import CONFIG_YML, ICON_LOOKUP_JSON, SETTINGS_VAR
from ..view.parse_colours import load_colours
from ..view.types import ColourChoice, HLGroups, Icons, Sortby
from .types import IgnoreOpts, MimetypeOptions, Settings, VersionCtlOpts, ViewOptions


@dataclass(frozen=True)
class _UserOptions:
    follow: bool
    lang: Optional[str]
    mimetypes: MimetypeOptions
    open_left: bool
    page_increment: int
    polling_rate: SupportsFloat
    session: bool
    show_hidden: bool
    version_control: VersionCtlOpts


@dataclass(frozen=True)
class _UserView:
    width: int
    sort_by: Sequence[Sortby]
    use_icons: Union[bool, Literal["emoji"]]
    colours: ColourChoice
    highlights: HLGroups
    time_format: str
    window_options: Mapping[str, Union[bool, str]]


@dataclass(frozen=True)
class _UserConfig:
    keymap: Mapping[str, AbstractSet[str]]
    options: _UserOptions
    view: _UserView
    ignore: IgnoreOpts


def _key_sort(keys: AbstractSet[str]) -> Sequence[str]:
    return sorted((key[len("CHAD") :] for key in keys), key=strxfrm)


def initial(nvim: Nvim, specs: Sequence[RpcSpec]) -> Settings:
    user_config = nvim.vars.get(SETTINGS_VAR, {})

    config: _UserConfig = decode(
        _UserConfig,
        merge(safe_load(CONFIG_YML.read_bytes()), hydrate(user_config), replace=True),
    )
    options, view = config.options, config.view

    icons: Icons = decode(Icons, loads(ICON_LOOKUP_JSON[view.use_icons].read_text()))
    hl_context = load_colours(
        nvim,
        colours=view.colours,
        particular_mappings=view.highlights,
    )

    view_opts = ViewOptions(
        hl_context=hl_context,
        icons=icons,
        sort_by=view.sort_by,
        use_icons=bool(view.use_icons),
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
        open_left=options.open_left,
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
