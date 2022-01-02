#!/usr/bin/env python3

from json import dump
from pathlib import Path
from subprocess import check_output
from sys import stdout

_LSC_SH = Path(__file__).parent.resolve(strict=True) / "lsc.sh"

_SOLARIZED = Path("dircolors-solarized").resolve(strict=True)
_NORD = Path("nord-dircolors").resolve(strict=True)
_TRAP_DOOR = Path("LS_COLORS").resolve(strict=True)

_PARSING = {
    _SOLARIZED / "dircolors.256dark": "solarized_dark_256",
    _SOLARIZED / "dircolors.ansi-dark": "solarized_dark",
    _SOLARIZED / "dircolors.ansi-light": "solarized_light",
    _SOLARIZED / "dircolors.ansi-universal": "solarized_universal",
    _NORD / "src" / "dir_colors": "nord",
    _TRAP_DOOR / "LS_COLORS": "trapdoor",
}


def main() -> None:
    lsc = {
        dest: check_output((str(_LSC_SH), str(file_name)), text=True)
        for file_name, dest in _PARSING.items()
    }
    dump(lsc, stdout, ensure_ascii=False, check_circular=False)


main()
