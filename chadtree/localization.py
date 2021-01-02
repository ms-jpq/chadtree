from locale import getdefaultlocale
from os.path import join
from string import Template
from typing import Dict, Optional, cast

from .da import load_json
from .logging import log

spec: Dict[str, str] = {}
fspec: Dict[str, str] = {}


def get_lang(code: Optional[str], fallback: str) -> str:
    if code:
        return code.lower()
    else:
        tag, _ = getdefaultlocale()
        tag = (tag or fallback).lower()
        primary, _, _ = tag.partition("-")
        lang, _, _ = primary.partition("_")
        return lang


def init(root: str, code: Optional[str], fallback: str) -> None:
    global spec, fspec
    lang = get_lang(code, fallback=fallback)
    ls, lf = f"{join(root, lang)}.json", f"{join(root, fallback)}.json"

    spec = cast(Dict[str, str], load_json(ls)) or {}
    fspec = cast(Dict[str, str], load_json(lf)) or {}


def LANG(key: str, **kwargs: str) -> str:
    template = spec.get(key, fspec[key])
    return Template(template).substitute(kwargs)
