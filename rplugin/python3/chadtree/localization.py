from locale import getdefaultlocale
from os.path import join
from string import Template
from typing import Dict, Optional, Protocol, cast

from .da import load_json

ISO_LANG = "C"


spec: Dict[str, str] = {}
dspec: Dict[str, str] = {}


def get_lang(code: Optional[str]) -> str:
    if code:
        return code
    else:
        tag, _ = getdefaultlocale()
        tag = tag or ISO_LANG
        primary, _, _ = tag.partition("-")
        lang = primary.upper()
        return lang


def init(root: str, code: Optional[str]) -> None:
    global spec, dspec
    lang = get_lang(code)
    ls, lf = join(root, lang), join(root, ISO_LANG)
    spec = cast(Dict[str, str], load_json(ls))
    dspec = cast(Dict[str, str], load_json(lf))


class Localizer(Protocol):
    def __call__(self, key: str, **kwargs: str) -> str:
        return ""


def localize() -> Localizer:
    def locale(key: str, **kwargs: str) -> str:
        template = spec.get(key, dspec[key])
        return Template(template).substitute(**kwargs)

    return locale
