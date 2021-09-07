from dataclasses import dataclass
from typing import Mapping, Optional, Sequence

from std2.pickle import new_decoder
from std2.urllib import urlopen
from yaml import safe_load

from chad_types import Hex, IconColours, IconColourSet

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
    decode = new_decoder[_GithubSpec](_GithubSpec, strict=False)

    raw = _fetch(_LINGUIST)
    yaml = decode(safe_load(raw))
    github: IconColours = {
        ext: spec.color
        for spec in yaml.values()
        for ext in spec.extensions
        if spec.color
    }
    colours = IconColourSet(github=github)
    return colours
