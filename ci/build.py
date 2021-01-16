#!/usr/bin/env python3

from dataclasses import dataclass
from datetime import datetime
from json import dump, load
from pathlib import Path
from subprocess import check_call, check_output, run
from typing import Any, Iterator, Mapping, Optional, Sequence

from std2.pickle import decode, encode
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

LANG_COLOURS_JSON = (ARTIFACTS / "github_colours").with_suffix(".json")
TEMP_JSON = (TEMP / "icons").with_suffix(".json")

SRC_ICONS = ("unicode_icons", "emoji_icons")
SRC_COLOUR = "colours"


@dataclass(frozen=True)
class GithubColours:
    extensions: Sequence[str] = ()
    color: Optional[str] = None


GithubSpec = Mapping[str, GithubColours]


@dataclass(frozen=True)
class IconFolderFormat:
    open: str
    closed: str


@dataclass(frozen=True)
class IconLoadFormat:
    extensions: Mapping[str, str]
    exact: Mapping[str, str]
    glob: Mapping[str, str]
    default: str
    folder: IconFolderFormat


@dataclass(frozen=True)
class IconDumpFormat:
    type: Mapping[str, str]
    name_exact: Mapping[str, str]
    name_glob: Mapping[str, str]
    default_icon: str
    folder: IconFolderFormat


@dataclass(frozen=True)
class ColoursLoadFormat:
    extensions: Mapping[str, str]
    exact: Mapping[str, str]
    glob: Mapping[str, str]


@dataclass(frozen=True)
class ColoursDumpFormat:
    type: Mapping[str, str]
    name_exact: Mapping[str, str]
    name_glob: Mapping[str, str]


def fetch(uri: str) -> str:
    with urlopen(uri) as resp:
        code = resp.getcode()
        body = resp.read()
    if code != 200:
        raise Exception(resp.headers, body)
    else:
        return body.decode()


def spit_json(path: Path, json: Any) -> None:
    path.parent.mkdir(exist_ok=True, parents=True)
    sorted_json = recur_sort(json)
    with path.open("w") as fd:
        dump(sorted_json, fd, ensure_ascii=False, check_circular=False, indent=2)


def process_exts(exts: Mapping[str, str]) -> Mapping[str, str]:
    return {f".{k}": v for k, v in exts.items()}


def process_glob(glob: Mapping[str, str]) -> Mapping[str, str]:
    return {k.rstrip("$").replace(r"\.", "."): v for k, v in glob.items()}


def process_icons(json: Any) -> IconDumpFormat:
    loaded: IconLoadFormat = decode(IconLoadFormat, json)
    dump = IconDumpFormat(
        type=process_exts(loaded.extensions),
        name_exact=loaded.exact,
        name_glob=process_glob(loaded.glob),
        default_icon=loaded.default,
        folder=loaded.folder,
    )
    return dump


def process_hexcode(colours: Mapping[str, str]) -> Mapping[str, str]:
    return {k: f"#{v}" for k, v in colours.items()}


def process_colours(json: Any) -> ColoursDumpFormat:
    loaded: ColoursLoadFormat = decode(ColoursLoadFormat, json)
    dump = ColoursDumpFormat(
        type=process_hexcode(process_exts(loaded.extensions)),
        name_exact=process_hexcode(loaded.exact),
        name_glob=process_hexcode(process_glob(loaded.glob)),
    )
    return dump


def devicons() -> None:
    TEMP.mkdir(parents=True, exist_ok=True)

    image = "chad-icons"
    time = format(datetime.now(), "%H-%M-%S")
    container = f"{image}-{time}"

    check_call(
        ("docker", "build", "-t", image, "-f", "Dockerfile", "."), cwd=DOCKER_PATH
    )
    check_call(("docker", "create", "--name", container, image))

    for icon in SRC_ICONS:
        src = f"{container}:/root/{icon}.json"
        check_call(("docker", "cp", src, str(TEMP_JSON)))

        parsed = process_icons(load(TEMP_JSON.open()))
        basic = safe_load((ASSETS / icon).with_suffix(".base.yml").read_bytes())
        merged = merge(encode(parsed), basic)

        dest = (ARTIFACTS / icon).with_suffix(".json")
        spit_json(dest, merged)

    ascii_json = "ascii_icons"
    json = safe_load((ASSETS / ascii_json).with_suffix(".base.yml").read_bytes())
    spit_json((ARTIFACTS / ascii_json).with_suffix(".json"), json)

    src = f"{container}:/root/{SRC_COLOUR}.json"
    dest = (ARTIFACTS / SRC_COLOUR).with_suffix(".json")
    check_call(("docker", "cp", src, str(TEMP_JSON)))
    parsed2 = process_colours(load(TEMP_JSON.open()))
    spit_json(dest, encode(parsed2))

    check_call(("docker", "rm", container))


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
    remote_brs = check_output(("git", "branch", "--remotes"), text=True)

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
        check_call(("git", "push", "--delete", "origin", *refs))

    proc = run(("git", "diff", "--exit-code"))
    if proc.returncode:
        time = datetime.now().strftime("%Y-%m-%d")
        brname = f"{prefix}--{time}"
        check_call(("git", "checkout", "-b", brname))
        check_call(("git", "add", "."))
        check_call(("git", "commit", "-m", f"update_icons: {time}"))
        check_call(("git", "push", "--set-upstream", "origin", brname))


def main() -> None:
    devicons()
    github_colours()
    # git_alert()


main()
