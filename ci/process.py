from typing import Mapping

from chad_types import Hex


def process_exts(exts: Mapping[str, str]) -> Mapping[str, str]:
    return {f".{k}": v for k, v in exts.items()}


def process_glob(glob: Mapping[str, str]) -> Mapping[str, str]:
    return {k.rstrip("$").replace(r"\.", "."): v for k, v in glob.items()}


def process_hexcode(colours: Mapping[str, str]) -> Mapping[str, Hex]:
    return {k: f"#{v}" for k, v in colours.items()}
