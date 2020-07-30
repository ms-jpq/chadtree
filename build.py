#!/usr/bin/env python3

from json import dump
from os.path import dirname, join, realpath
from typing import Dict
from urllib.request import urlopen

from yaml import safe_load

__dir__ = dirname(realpath(__file__))
ARTIFACTS = join(__dir__, "artifacts")


LANG_COLOURS = """
https://raw.githubusercontent.com/github/linguist/master/lib/linguist/languages.yml
"""
LANG_COLOURS_JSON = join(ARTIFACTS, "github_colours.json")


def fetch(uri: str) -> str:
    with urlopen(uri) as resp:
        ret = resp.read().decode()
        return ret


def github_colours() -> Dict[str, str]:
    raw = fetch(LANG_COLOURS)
    yaml = safe_load(raw)
    lookup = {
        ext: colour
        for val in yaml.values()
        for ext in val.get("extensions", ())
        if (colour := val.get("color"))
    }
    return lookup


def main() -> None:
    lookup = github_colours()
    with open(LANG_COLOURS_JSON, "w") as fd:
        dump(lookup, fd, ensure_ascii=False, check_circular=False, indent=2)


main()
