#!/usr/bin/env python3

from datetime import datetime
from json import dump
from os import getcwd
from os.path import dirname, join, realpath
from subprocess import run
from typing import Dict
from urllib.request import urlopen

from yaml import safe_load

__dir__ = dirname(realpath(__file__))
ARTIFACTS = join(__dir__, "artifacts")
ICONS_PATH = join(__dir__, "docker", "icons")


LANG_COLOURS = """
https://raw.githubusercontent.com/github/linguist/master/lib/linguist/languages.yml
"""

LANG_COLOURS_JSON = join(ARTIFACTS, "github_colours.json")
ICONS_JSON = join(ARTIFACTS, "devicons.json")


def call(prog: str, *args: str, cwd: str = getcwd()) -> None:
    ret = run([prog, *args], cwd=cwd)
    if ret.returncode != 0:
        exit(ret.returncode)


def devicons() -> None:
    image = "chad-icons"
    time = datetime.now().strftime("%H-%M-%S")
    container = f"{image}-{time}"
    src = f"{container}:/root/icons.json"
    call("docker", "build", "-t", image, "-f", "Dockerfile", ".", cwd=ICONS_PATH)
    call("docker", "create", "--name", container, image)
    call("docker", "cp", src, ICONS_JSON)
    call("docker", "rm", container)


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
    devicons()
    lookup = github_colours()
    with open(LANG_COLOURS_JSON, "w") as fd:
        dump(lookup, fd, ensure_ascii=False, check_circular=False, indent=2)


main()
