#!/usr/bin/env python3

from asyncio import run as aio_run
from dataclasses import dataclass
from datetime import datetime
from json import dump, load
from os import PathLike, getcwd
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
    Union,
)

from std2.pickle import decode
from std2.tree import merge, recur_sort
from std2.urllib import urlopen
from yaml import safe_load

_TOP_LV = Path(__file__).resolve().parent.parent
TEMP = _TOP_LV / "temp"
ASSETS = _TOP_LV / "assets"
ARTIFACTS = _TOP_LV / "artifacts"
DOCKER_PATH = _TOP_LV / "ci" / "docker"


LANG_COLOURS = """
https://raw.githubusercontent.com/github/linguist/master/lib/linguist/languages.yml
"""

LANG_COLOURS_JSON = ARTIFACTS / "github_colours"
TEMP_JSON = TEMP / "icons"

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


def call(prog: str, *args: str, cwd: Union[str, PathLike] = getcwd()) -> None:
    ret = run((prog, *args), cwd=cwd)
    if ret.returncode != 0:
        exit(ret.returncode)


def fetch(uri: str) -> str:
    resp = aio_run(urlopen(uri))
    return resp.read().decode()


def slurp_json(path: Path) -> Any:
    with path.with_suffix(".json").open() as fd:
        return load(fd)


def spit_json(path: Path, json: Any) -> None:
    path.parent.mkdir(exist_ok=True, parents=True)
    sorted_json = recur_sort(json)
    with path.with_suffix(".json").open("w") as fd:
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
    TEMP.mkdir(parents=True, exist_ok=True)

    image = "chad-icons"
    time = format(datetime.now(), "%H-%M-%S")
    container = f"{image}-{time}"

    call("docker", "build", "-t", image, "-f", "Dockerfile", ".", cwd=DOCKER_PATH)
    call("docker", "create", "--name", container, image)

    for icon in SRC_ICONS:
        src = f"{container}:/root/{icon}.json"
        dest = str(TEMP_JSON.with_suffix(".json"))
        call("docker", "cp", src, dest)

        json = slurp_json(TEMP_JSON)
        basic = slurp_json(ASSETS / f"{icon}.base")
        parsed = process_json(json)
        merged = merge(parsed, basic)

        final_dest = ARTIFACTS / icon
        spit_json(final_dest, merged)

    ascii_json = "ascii_icons"
    json = slurp_json(ASSETS / f"{ascii_json}.base")
    spit_json(ARTIFACTS / ascii_json, json)
    call("docker", "rm", container)


def github_colours() -> None:
    raw = fetch(LANG_COLOURS)
    yaml: GithubSpec = decode(GithubSpec, safe_load(raw), strict=False)
    lookup: Mapping[str, str] = {
        ext: spec.color
        for spec in yaml.values()
        for ext in spec.extensions
        if spec.color
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
        time = datetime.now().strftime("%Y-%m-%d")
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
