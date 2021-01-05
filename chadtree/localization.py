from locale import getdefaultlocale
from string import Template
from typing import Mapping, MutableMapping, Optional

from std2.pickle.decode import decode
from std2.tree import merge

from .consts import DEFAULT_LANG, LANG_ROOT
from .da import load_json


def _get_lang(code: Optional[str], fallback: str) -> str:
    if code:
        return code.casefold()
    else:
        tag, _ = getdefaultlocale()
        tag = (tag or fallback).casefold()
        primary, _, _ = tag.partition("-")
        lang, _, _ = primary.partition("_")
        return lang


class Lang:
    def __init__(self, specs: MutableMapping[str, str]) -> None:
        self._specs = specs

    def __call__(self, key: str, **kwds: str) -> str:
        spec = self._specs[key]
        return Template(spec).substitute(kwds)


LANG = Lang({})


def init(code: Optional[str]) -> None:
    lang = _get_lang(code, fallback=DEFAULT_LANG)

    lf = (LANG_ROOT / DEFAULT_LANG).with_suffix(".json")
    ls = (LANG_ROOT / lang).with_suffix(".json")
    specs: Mapping[str, str] = decode(
        Mapping[str, str], merge(load_json(lf) or {}, load_json(ls) or {})
    )
    LANG._specs.update(specs)
