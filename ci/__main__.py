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



from .text_decorations import load_text_decors


load_text_decors()