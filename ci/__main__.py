from json import dump
from pathlib import Path
from typing import Any

from chad_types import ARTIFACT
from std2.pickle import encode
from std2.tree import recur_sort

from .text_decorations import load_text_decors
from .ls_colours import load_ls_colours
from .icon_colours import load_icon_colours

def _spit_json(path: Path, json: Any) -> None:
    path.parent.mkdir(exist_ok=True, parents=True)
    sorted_json = recur_sort(json)
    with path.open("w") as fd:
        dump(sorted_json, fd, ensure_ascii=False, check_circular=False, indent=2)


load_text_decors()
