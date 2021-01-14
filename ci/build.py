#!/usr/bin/env python3

from dataclasses import dataclass
from datetime import datetime
from http.client import HTTPResponse
from json import dump, load
from locale import strxfrm
from os import getcwd, makedirs
from os.path import join
from pathlib import Path
from subprocess import PIPE, run
from typing import (
    AbstractSet,
    Any,
    Iterator,
    Mapping,
    MutableMapping,
    Optional,
    Sequence,
    cast,
)
from urllib.request import urlopen

from std2.tree import merge, recur_sort
from yaml import safe_load

__dir__ = Path(__file__).resolve().parent.parent
TEMP = join(__dir__, "temp")
ASSETS = join(__dir__, "assets")
ARTIFACTS = join(__dir__, "artifacts")
DOCKER_PATH = join(__dir__, "ci", "docker")


LANG_COLOURS = """
https://raw.githubusercontent.com/github/linguist/master/lib/linguist/languages.yml
"""

LANG_COLOURS_JSON = join(ARTIFACTS, "github_colours")
TEMP_JSON = join(TEMP, "icons")

SRC_ICONS = ("unicode_icons", "emoji_icons")


@dataclass(frozen=True)
class GithubColours:
    extensions: Sequence[str] = ()
    color: Optional[str] = None


GithubSpec = Mapping[str, GithubColours]


@dataclass(frozen=True)
class DumpFormat:
    type: Mapping[str, str]
    name_exact: AbstractSet[str]
    name_glob: AbstractSet[str]


def call(prog: str, *args: str, cwd: str = getcwd()) -> None:
    ret = run((prog, *args), cwd=cwd)
    if ret.returncode != 0:
        exit(ret.returncode)


def fetch(uri: str) -> str:
    with urlopen(uri) as resp:
        ret = cast(HTTPResponse, resp).read().decode()
        return ret


def slurp_json(path: str) -> Any:
    with open(f"{path}.json") as fd:
        return load(fd)


def spit_json(path: str, json: Any) -> None:
    sorted_json = recur_sort(json)
    with open(f"{path}.json", "w") as fd:
        dump(sorted_json, fd, ensure_ascii=False, check_circular=False, indent=2)


def process_json(
    json: Mapping[str, Mapping[str, str]]
) -> Mapping[str, Mapping[str, str]]:
    new: MutableMapping[str, Mapping[str, str]] = {}
    new["type"] = {f".{k}": v for k, v in json["extensions"].items()}
    new["name_exact"] = json["exact"]
    new["name_glob"] = {
        k.rstrip("$").replace(r"\.", "."): v for k, v in json["glob"].items()
    }
    new["default_icon"] = json["default"]
    new["folder"] = json["folder"]
    return new


def devicons() -> None:
    image = "chad-icons"
    time = format(datetime.now(), "%H-%M-%S")
    container = f"{image}-{time}"

    makedirs(TEMP, exist_ok=True)
    call("docker", "build", "-t", image, "-f", "Dockerfile", ".", cwd=DOCKER_PATH)
    call("docker", "create", "--name", container, image)
    for icon in SRC_ICONS:
        src = f"{container}:/root/{icon}.json"
        call("docker", "cp", src, f"{TEMP_JSON}.json")
        json = slurp_json(TEMP_JSON)
        basic = slurp_json(join(ASSETS, f"{icon}.base"))
        parsed = process_json(json)
        merged = merge(parsed, basic)
        dest = join(ARTIFACTS, icon)
        spit_json(dest, merged)
    ascii_json = "ascii_icons"
    json = slurp_json(join(ASSETS, f"{ascii_json}.base"))
    spit_json(join(ARTIFACTS, ascii_json), json)
    call("docker", "rm", container)


def github_colours() -> None:
    raw = fetch(LANG_COLOURS)
    yaml = safe_load(raw)
    lookup = {
        ext: colour
        for ext, colour in (
            (ext, val.get("color"))
            for val in yaml.values()
            for ext in val.get("extensions", ())
        )
        if colour
    }

    spit_json(LANG_COLOURS_JSON, lookup)


def git_alert() -> None:
    prefix = "update-icons"
    proc = run(("git", "branch", "--remotes"), stdout=PIPE, check=True)
    remote_brs = proc.stdout.decode()

    print("DEBUG")
    print([remote_brs])

    def cont() -> Iterator[str]:
        for br in remote_brs.splitlines():
            b = br.strip()
            if b and "->" not in b:
                _, _, name = b.partition("/")
                if name.startswith(prefix):
                    yield name

    refs = tuple(cont())
    print(refs)
    if refs:
        call("git", "push", "--delete", "origin", *refs)

    proc = run(("git", "diff", "--exit-code"))
    if proc.returncode:
        time = format(datetime.now(), "%Y-%m-%d")
        brname = f"{prefix}--{time}"
        call("git", "checkout", "-b", brname)
        call("git", "add", ".")
        call("git", "commit", "-m", f"update_icons: {time}")
        call("git", "push", "--set-upstream", "origin", brname)


def main() -> None:
    devicons()
    github_colours()
    git_alert()


main()
