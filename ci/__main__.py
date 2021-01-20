from dataclasses import dataclass
from datetime import datetime
from json import dump, load
from pathlib import Path
from subprocess import check_call, check_output, run
from typing import Any, Iterator, Mapping, Optional, Sequence

from std2.coloursys import hex_inverse
from std2.pickle import decode, encode
from std2.tree import merge, recur_sort
from std2.urllib import urlopen
from yaml import safe_load

_TOP_LV = Path(__file__).resolve().parent.parent
_CI = _TOP_LV / "ci"
_TEMP = _TOP_LV / "temp"
_ASSETS = _TOP_LV / "assets"
_ARTIFACTS = _TOP_LV / "artifacts"
_DOCKER_PATH = _CI / "docker"
_LSC_EVAL = _CI / "lsc.sh"


_LANG_COLOURS = """
https://raw.githubusercontent.com/github/linguist/master/lib/linguist/languages.yml
"""

_LANG_COLOURS_JSON = (_ARTIFACTS / "github_colours").with_suffix(".json")
_TEMP_JSON = (_TEMP / "icons").with_suffix(".json")

_SRC_ICONS = ("unicode_icons", "emoji_icons")
_SRC_COLOUR = "colours"


@dataclass(frozen=True)
class _GithubColours:
    extensions: Sequence[str] = ()
    color: Optional[str] = None


GithubSpec = Mapping[str, _GithubColours]


@dataclass(frozen=True)
class _IconFolderFormat:
    open: str
    closed: str


@dataclass(frozen=True)
class _IconLoadFormat:
    extensions: Mapping[str, str]
    exact: Mapping[str, str]
    glob: Mapping[str, str]
    default: str
    folder: _IconFolderFormat


@dataclass(frozen=True)
class _IconDumpFormat:
    ext_exact: Mapping[str, str]
    name_exact: Mapping[str, str]
    name_glob: Mapping[str, str]
    default_icon: str
    folder: _IconFolderFormat


@dataclass(frozen=True)
class _ColoursLoadFormat:
    extensions: Mapping[str, str]
    exact: Mapping[str, str]
    glob: Mapping[str, str]


@dataclass(frozen=True)
class _ColoursDumpFormat:
    ext_exact: Mapping[str, str]
    name_exact: Mapping[str, str]
    name_glob: Mapping[str, str]


def _fetch(uri: str) -> str:
    with urlopen(uri) as resp:
        code = resp.getcode()
        body = resp.read()
    if code != 200:
        raise Exception(resp.headers, body)
    else:
        return body.decode()


def _spit_json(path: Path, json: Any) -> None:
    path.parent.mkdir(exist_ok=True, parents=True)
    sorted_json = recur_sort(json)
    with path.open("w") as fd:
        dump(sorted_json, fd, ensure_ascii=False, check_circular=False, indent=2)


def _process_exts(exts: Mapping[str, str]) -> Mapping[str, str]:
    return {f".{k}": v for k, v in exts.items()}


def _process_glob(glob: Mapping[str, str]) -> Mapping[str, str]:
    return {k.rstrip("$").replace(r"\.", "."): v for k, v in glob.items()}


def _process_icons(json: Any) -> _IconDumpFormat:
    loaded: _IconLoadFormat = decode(_IconLoadFormat, json)
    dump = _IconDumpFormat(
        ext_exact=_process_exts(loaded.extensions),
        name_exact=loaded.exact,
        name_glob=_process_glob(loaded.glob),
        default_icon=loaded.default,
        folder=loaded.folder,
    )
    return dump


def _process_hexcode(colours: Mapping[str, str]) -> Mapping[str, str]:
    return {k: f"#{v}" for k, v in colours.items()}


def _process_colours(json: Any) -> _ColoursDumpFormat:
    loaded: _ColoursLoadFormat = decode(_ColoursLoadFormat, json)
    dump = _ColoursDumpFormat(
        ext_exact=_process_hexcode(_process_exts(loaded.extensions)),
        name_exact=_process_hexcode(loaded.exact),
        name_glob=_process_hexcode(_process_glob(loaded.glob)),
    )
    return dump


def _trans_inverse(mapping: Mapping[str, str]) -> Mapping[str, str]:
    return {key: hex_inverse(val) for key, val in mapping.items()}


def _invert_nightmode(night_mode: _ColoursDumpFormat) -> _ColoursDumpFormat:
    dump = _ColoursDumpFormat(
        ext_exact=_trans_inverse(night_mode.ext_exact),
        name_exact=_trans_inverse(night_mode.name_exact),
        name_glob=_trans_inverse(night_mode.name_glob),
    )
    return dump


def _devicons() -> None:
    _TEMP.mkdir(parents=True, exist_ok=True)

    image = "chad-icons"
    time = format(datetime.now(), "%H-%M-%S")
    container = f"{image}-{time}"

    check_call(
        ("docker", "build", "-t", image, "-f", "Dockerfile", "."), cwd=_DOCKER_PATH
    )
    check_call(("docker", "create", "--name", container, image))

    for icon in _SRC_ICONS:
        src = f"{container}:/root/{icon}.json"
        check_call(("docker", "cp", src, str(_TEMP_JSON)))

        parsed = _process_icons(load(_TEMP_JSON.open()))
        basic = safe_load((_ASSETS / icon).with_suffix(".base.yml").read_bytes())
        merged = merge(encode(parsed), basic)

        dest = (_ARTIFACTS / icon).with_suffix(".json")
        _spit_json(dest, merged)

    ascii_json = "ascii_icons"
    json = safe_load((_ASSETS / ascii_json).with_suffix(".base.yml").read_bytes())
    _spit_json((_ARTIFACTS / ascii_json).with_suffix(".json"), json)

    src = f"{container}:/root/{_SRC_COLOUR}.json"
    check_call(("docker", "cp", src, str(_TEMP_JSON)))
    night_mode = _process_colours(load(_TEMP_JSON.open()))
    day_mode = _invert_nightmode(night_mode)

    night_dest = (_ARTIFACTS / f"{_SRC_COLOUR}_night").with_suffix(".json")
    day_dest = (_ARTIFACTS / f"{_SRC_COLOUR}_day").with_suffix(".json")

    _spit_json(night_dest, encode(night_mode))
    _spit_json(day_dest, encode(day_mode))
    check_call(("docker", "rm", container))


def _github_colours() -> None:
    raw = _fetch(_LANG_COLOURS)
    yaml: GithubSpec = decode(GithubSpec, safe_load(raw), strict=False)
    lookup: Mapping[str, str] = {
        ext: spec.color
        for spec in yaml.values()
        for ext in spec.extensions
        if spec.color
    }

    _spit_json(_LANG_COLOURS_JSON, lookup)


def _ls_colours() -> None:
    pass




def main() -> None:
    _devicons()
    _github_colours()
    _ls_colours()
    # _git_alert()


main()
