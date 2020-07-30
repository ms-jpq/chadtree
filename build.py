#!/usr/bin/env python3

from datetime import datetime
from json import dump, load
from locale import strxfrm
from os import getcwd, makedirs
from os.path import dirname, join, realpath
from subprocess import run
from typing import Any, Dict
from urllib.request import urlopen

from yaml import safe_load

__dir__ = dirname(realpath(__file__))
TEMP = join(__dir__, "temp")
ARTIFACTS = join(__dir__, "artifacts")
DOCKER_PATH = join(__dir__, "docker", "icons")


LANG_COLOURS = """
https://raw.githubusercontent.com/github/linguist/master/lib/linguist/languages.yml
"""

LANG_COLOURS_JSON = join(ARTIFACTS, "github_colours.json")
TEMP_JSON = join(TEMP, "icons.json")
ICONS_JSON = join(ARTIFACTS, "icons.json")


def call(prog: str, *args: str, cwd: str = getcwd()) -> None:
    ret = run([prog, *args], cwd=cwd)
    if ret.returncode != 0:
        exit(ret.returncode)


def fetch(uri: str) -> str:
    with urlopen(uri) as resp:
        ret = resp.read().decode()
        return ret


def recur_sort(data: Any) -> Any:
    if type(data) is dict:
        return {k: recur_sort(data[k]) for k in sorted(data, key=strxfrm)}
    elif type(data) is list:
        return [recur_sort(el) for el in data]
    else:
        return data


def spit_json(path: str, json: Any) -> None:
    sorted_json = recur_sort(json)
    with open(path, "w") as fd:
        dump(sorted_json, fd, ensure_ascii=False, check_circular=False, indent=2)


def process_json(json: Dict[str, Dict[str, str]]) -> Dict[str, Dict[str, str]]:
    new = {}
    new["type"] = {f".{k}": v for k, v in json["extensions"].items()}
    new["name"] = json["exact"]
    return new


def devicons() -> None:
    image = "chad-icons"
    time = datetime.now().strftime("%H-%M-%S")
    container = f"{image}-{time}"
    src = f"{container}:/root/icons.json"

    makedirs(TEMP, exist_ok=True)
    call("docker", "build", "-t", image, "-f", "Dockerfile", ".", cwd=DOCKER_PATH)
    call("docker", "create", "--name", container, image)
    call("docker", "cp", src, TEMP_JSON)
    call("docker", "rm", container)

    with open(TEMP_JSON) as fd:
        json = load(fd)
        parsed = process_json(json)
        spit_json(ICONS_JSON, parsed)


def github_colours() -> None:
    raw = fetch(LANG_COLOURS)
    yaml = safe_load(raw)
    lookup = {
        ext: colour
        for val in yaml.values()
        for ext in val.get("extensions", ())
        if (colour := val.get("color"))
    }

    spit_json(LANG_COLOURS_JSON, lookup)


def main() -> None:
    devicons()
    github_colours()


main()
