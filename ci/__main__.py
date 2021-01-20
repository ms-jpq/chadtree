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
from chad_types import Icons, TOP_LEVEL, ARTIFACT

_ASSETS = TOP_LEVEL / "assets"


def _spit_json(path: Path, json: Any) -> None:
    path.parent.mkdir(exist_ok=True, parents=True)
    sorted_json = recur_sort(json)
    with path.open("w") as fd:
        dump(sorted_json, fd, ensure_ascii=False, check_circular=False, indent=2)


def _process_exts(exts: Mapping[str, str]) -> Mapping[str, str]:
    return {f".{k}": v for k, v in exts.items()}


def _process_glob(glob: Mapping[str, str]) -> Mapping[str, str]:
    return {k.rstrip("$").replace(r"\.", "."): v for k, v in glob.items()}


def _process_hexcode(colours: Mapping[str, str]) -> Mapping[str, str]:
    return {k: f"#{v}" for k, v in colours.items()}


# def _process_colours(json: Any) -> _ColoursDumpFormat:
#     loaded: _ColoursLoadFormat = decode(_ColoursLoadFormat, json)
#     dump = _ColoursDumpFormat(
#         ext_exact=_process_hexcode(_process_exts(loaded.extensions)),
#         name_exact=_process_hexcode(loaded.exact),
#         name_glob=_process_hexcode(_process_glob(loaded.glob)),
#     )
#     return dump


# def _trans_inverse(mapping: Mapping[str, str]) -> Mapping[str, str]:
#     return {key: hex_inverse(val) for key, val in mapping.items()}


# def _invert_nightmode(night_mode: _ColoursDumpFormat) -> _ColoursDumpFormat:
#     dump = _ColoursDumpFormat(
#         ext_exact=_trans_inverse(night_mode.ext_exact),
#         name_exact=_trans_inverse(night_mode.name_exact),
#         name_glob=_trans_inverse(night_mode.name_glob),
#     )
#     return dump

#  image = "chad-icons"
#     time = format(datetime.now(), "%H-%M-%S")
#     container = f"{image}-{time}"

#     check_call(
#         ("docker", "build", "-t", image, "-f", "Dockerfile", "."), cwd=_DOCKER_PATH
#     )
#     check_call(("docker", "run", "--rm", image))
