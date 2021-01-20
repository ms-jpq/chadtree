#!/usr/bin/env python3

from json import dump
from pathlib import Path
from subprocess import check_output
from sys import stdout
from typing import Mapping, cast


_LSC_SH = Path(__file__).parent.resolve() / "lsc.sh"

_SOLARIZED = Path("dircolors-solarized").resolve()
_NORD = Path("nord-dircolors").resolve()

_PARSING = {
    _SOLARIZED / "dircolors.256dark": "dark_256",
    _SOLARIZED / "dircolors.ansi-dark": "ansi_dark",
    _SOLARIZED / "dircolors.ansi-light": "ansi_light",
    _SOLARIZED / "dircolors.ansi-universal": "ansi_universal",
    _NORD / "src" / "dir_colors": "nord",
}


def _load_lsc() -> Mapping[str, str]:
    return {
        dest: check_output((str(_LSC_SH), str(file_name)), text=True)
        for file_name, dest in _PARSING.items()
    }


def main() -> None:
    lsc = _load_lsc()
    dump(lsc, stdout, ensure_ascii=False, check_circular=False)


main()
