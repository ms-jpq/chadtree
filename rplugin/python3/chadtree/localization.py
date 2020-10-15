from locale import getdefaultlocale
from os.path import join
from string import Template
from typing import Dict, Optional, Protocol, cast

from .da import load_json

spec: Dict[str, str] = {}
fspec: Dict[str, str] = {}


def get_lang(code: Optional[str], fallback: str) -> str:
    if code:
        return code
    else:
        tag, _ = getdefaultlocale()
        tag = tag or fallback
        primary, _, _ = tag.partition("-")
        lang = primary.upper()
        return lang


def init(root: str, code: Optional[str], fallback: str) -> None:
    global spec, fspec
    lang = get_lang(code, fallback=fallback)
    ls, lf = join(root, lang), join(root, fallback)

    spec = cast(Dict[str, str], load_json(ls))
    fspec = cast(Dict[str, str], load_json(lf))


class Localizer(Protocol):
    def __call__(self, key: str, **kwargs: str) -> str:
        return ""


def localize() -> Localizer:
    def locale(key: str, **kwargs: str) -> str:
        template = spec.get(key, fspec[key])
        return Template(template).substitute(**kwargs)

    return locale
