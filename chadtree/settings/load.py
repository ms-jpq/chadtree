from dataclasses import dataclass
from enum import Enum, auto
from locale import strxfrm
from typing import (
    AbstractSet,
    Any,
    Iterable,
    Mapping,
    Optional,
    Sequence,
    SupportsFloat,
    Union,
    cast,
)

from pynvim_pp.atomic import Atomic
from pynvim_pp.nvim import Nvim
from pynvim_pp.types import NoneType, RPCallable
from pynvim_pp.window import Window
from std2.configparser import hydrate
from std2.graphlib import merge
from std2.pickle.decoder import new_decoder
from std2.pickle.types import DecodeError
from yaml import safe_load

from chad_types import (
    ARTIFACT,
    Artifact,
    IconColourSetEnum,
    IconGlyphSetEnum,
    LSColoursEnum,
    TextColourSetEnum,
)

from ..consts import CONFIG_YML, SETTINGS_VAR
from ..fs.types import Ignored
from ..registry import NAMESPACE
from ..view.load import load_theme
from ..view.types import HLGroups, Sortby, ViewOptions
from .types import MimetypeOptions, Settings, VersionCtlOpts


class _OpenDirection(Enum):
    left = auto()
    right = auto()


@dataclass(frozen=True)
class _UserOptions:
    close_on_open: bool
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
    xdg: bool
    profiling: bool


async def initial(specs: Iterable[RPCallable]) -> Settings:
    a_decode = new_decoder[Artifact](Artifact)
    c_decode = new_decoder[_UserConfig](_UserConfig)

    win = await Window.get_current()
    artifacts = a_decode(safe_load(ARTIFACT.read_text("UTF-8")))

    user_config = cast(
        Mapping[str, Any], await Nvim.vars.get(NoneType, SETTINGS_VAR) or {}
    )
    config = c_decode(
        merge(
            safe_load(CONFIG_YML.read_text("UTF-8")), hydrate(user_config), replace=True
        )
    )
    options, view, theme = config.options, config.view, config.theme

    atomic = Atomic()
    for opt in view.window_options:
        atomic.win_get_option(win, opt)
    win_opts = cast(Sequence[Union[bool, str]], await atomic.commit(NoneType))
    win_actual_opts = {k: v for k, v in zip(view.window_options, win_opts)}

    icons, hl_context = load_theme(
        artifact=artifacts,
        particular_mappings=theme.highlights,
        discrete_colours=theme.discrete_colour_map,
        icon_set=theme.icon_glyph_set,
        icon_colour_set=theme.icon_colour_set,
        text_colour_set=theme.text_colour_set,
    )

    use_icons = theme.icon_glyph_set not in {
        IconGlyphSetEnum.ascii,
        IconGlyphSetEnum.ascii_hollow,
    }

    view_opts = ViewOptions(
        hl_context=hl_context,
        icons=icons,
        sort_by=view.sort_by,
        use_icons=use_icons,
        time_fmt=view.time_format,
    )

    keymap = {f"{NAMESPACE}.{k.capitalize()}": v for k, v in config.keymap.items()}
    legal_keys = {f"{NAMESPACE}.{spec.method.capitalize()}" for spec in specs}
    extra_keys = keymap.keys() - legal_keys

    if extra_keys:
        raise DecodeError(
            path=(_UserOptions, sorted(legal_keys, key=strxfrm)),
            actual=None,
            missing_keys=(),
            extra_keys=sorted(extra_keys, key=strxfrm),
        )

    else:
        settings = Settings(
            close_on_open=options.close_on_open,
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
            win_actual_opts=win_actual_opts,
            win_local_opts=view.window_options,
            xdg=config.xdg,
            profiling=config.profiling,
        )

        return settings
