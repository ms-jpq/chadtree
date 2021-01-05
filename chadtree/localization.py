from locale import getdefaultlocale
from string import Template
from typing import MutableMapping, Optional, cast
from pathlib import Path
from .da import load_json

spec: MutableMapping[str, str] = {}
fspec: MutableMapping[str, str] = {}


def _get_lang(code: Optional[str], fallback: str) -> str:
    if code:
        return code.lower()
    else:
        tag, _ = getdefaultlocale()
        tag = (tag or fallback).lower()
        primary, _, _ = tag.partition("-")
        lang, _, _ = primary.partition("_")
        return lang


def init(root: Path, code: Optional[str], fallback: str) -> None:
    global spec, fspec

    lang = _get_lang(code, fallback=fallback)
    ls, lf = (root / lang).with_suffix("json"), (root / fallback).with_suffix("json")

    spec = cast(MutableMapping[str, str], load_json(ls)) or {}
    fspec = cast(MutableMapping[str, str], load_json(lf)) or {}


def LANG(key: str, **kwargs: str) -> str:
    template = spec.get(key, fspec[key])
    return Template(template).substitute(kwargs)
