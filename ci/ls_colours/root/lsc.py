#!/usr/bin/env python3

from argparse import ArgumentParser, Namespace
from json import dump
from pathlib import Path
from subprocess import check_output
from sys import stdout
from typing import Mapping, cast

_LSC_SH = Path(__file__).parent.resolve() / "lsc.sh"
_PARSING = {
    "dircolors.256dark": "dark_256",
    "dircolors.ansi-dark": "ansi_dark",
    "dircolors.ansi-light": "ansi_light",
    "dircolors.ansi-universal": "ansi_universal",
}


def _parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("top_level", type=Path)
    return parser.parse_args()


def _load_lsc(top_level: Path) -> Mapping[str, str]:
    return {
        dest: check_output((str(_LSC_SH), file_name), text=True, cwd=top_level)
        for file_name, dest in _PARSING.items()
    }


def main() -> None:
    args = _parse_args()
    top_level = cast(Path, args.top_level).resolve()
    lsc = _load_lsc(top_level)
    dump(lsc, stdout, ensure_ascii=False, check_circular=False)


main()
