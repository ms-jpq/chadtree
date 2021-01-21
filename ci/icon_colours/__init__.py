from dataclasses import dataclass
from typing import Mapping, Optional, Sequence

from chad_types import Hex, IconColours, IconColourSet
from std2.pickle import decode
from std2.urllib import urlopen
from yaml import safe_load

_LINGUIST = """
https://raw.githubusercontent.com/github/linguist/master/lib/linguist/languages.yml
"""


@dataclass(frozen=True)
class _GithubColours:
    extensions: Sequence[str] = ()
    color: Optional[Hex] = None


_GithubSpec = Mapping[str, _GithubColours]


def _fetch(uri: str) -> str:
    with urlopen(uri) as resp:
        code = resp.getcode()
        body = resp.read()
    if code != 200:
        raise Exception(resp.headers, body)
    else:
        return body.decode()


def load_icon_colours() -> IconColourSet:
    raw = _fetch(_LINGUIST)
    yaml: _GithubSpec = decode(_GithubSpec, safe_load(raw), strict=False)
    github: IconColours = {
        ext: spec.color
        for spec in yaml.values()
        for ext in spec.extensions
        if spec.color
    }
    colours = IconColourSet(github=github)
    return colours
