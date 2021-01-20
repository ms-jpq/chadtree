from json import loads
from pathlib import Path
from typing import Mapping, Tuple

from chad_types import ASSETS, Hex, Icons, IconSet, TextColours, TextColourSet
from std2.pickle import decode
from std2.tree import merge
from yaml import safe_load

from ..run import docker_run

_DOCKERFILE = Path(__file__).resolve().parent / "Dockerfile"
_ICON_BASE = ASSETS / "icon_base.yml"


def _process_exts(exts: Mapping[str, str]) -> Mapping[str, str]:
    return {f".{k}": v for k, v in exts.items()}


def _process_glob(glob: Mapping[str, str]) -> Mapping[str, str]:
    return {k.rstrip("$").replace(r"\.", "."): v for k, v in glob.items()}


def _process_hexcode(colours: Mapping[str, str]) -> Mapping[str, Hex]:
    return {k: f"#{v}" for k, v in colours.items()}


def _process_icons(icons: Icons) -> Icons:
    return Icons(
        default_icon=icons.default_icon,
        folder=icons.folder,
        link=icons.link,
        status=icons.status,
        ext_exact=_process_exts(icons.ext_exact),
        name_exact=icons.name_exact,
        name_glob=_process_glob(icons.name_glob),
    )


def _process_colours(colours: TextColours) -> TextColours:
    return TextColours(
        ext_exact=_process_hexcode(_process_exts(colours.ext_exact)),
        name_exact=_process_hexcode(colours.name_exact),
        name_glob=_process_hexcode(_process_glob(colours.name_glob)),
    )


def load_text_decors() -> Tuple[IconSet, TextColourSet]:
    yaml = safe_load(_ICON_BASE.read_bytes())
    json = loads(docker_run(_DOCKERFILE))
    data = merge(json, yaml)
    icon_spec: IconSet = decode(IconSet, data, strict=False)
    icon_set = IconSet(
        ascii=_process_icons(icon_spec.ascii),
        devicons=_process_icons(icon_spec.devicons),
        emoji=_process_icons(icon_spec.emoji),
    )
    colour_spec: TextColourSet = decode(TextColourSet, data, strict=False)
    colour_set = TextColourSet(
        nerdtree_syntax=_process_colours(colour_spec.nerdtree_syntax)
    )
    return icon_set, colour_set
