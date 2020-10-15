from locale import getdefaultlocale
from string import Template
from typing import Dict, Protocol

ISO_LANG = "C"


def get_lang() -> str:
    tag, _ = getdefaultlocale()
    tag = tag or ISO_LANG
    primary, _, _ = tag.partition("-")
    lang = primary.upper()
    return lang


class Localizer(Protocol):
    def __call__(self, key: str, **kwargs: str) -> str:
        return ""


def localize(root: str) -> Localizer:
    lang = get_lang()
    specs: Dict[str, Dict[str, str]] = {}
    spec, dspec = specs[lang], specs[ISO_LANG]

    def locale(key: str, **kwargs: str) -> str:
        template = spec.get(key, dspec[key])
        return Template(template).substitute(**kwargs)

    return locale
