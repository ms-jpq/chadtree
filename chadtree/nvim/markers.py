from collections import Counter
from itertools import chain
from os.path import normcase
from pathlib import Path, PurePath
from string import ascii_uppercase
from typing import AbstractSet, Iterator, Mapping, MutableMapping, MutableSet, Optional
from urllib.parse import urlsplit

from pynvim import Nvim
from pynvim_pp.api import get_cwd

from ..fs.ops import ancestors
from .types import Markers


def _resolve(cwd: PurePath, path: str) -> Optional[PurePath]:
    try:
        parsed = urlsplit(path)
    except ValueError:
        return None
    else:
        if parsed.scheme not in {"", "file"}:
            return None
        else:
            safe_path = Path(normcase(parsed.path))

            if safe_path.is_absolute():
                return safe_path
            elif (resolved := safe_path.expanduser()) != safe_path:
                return resolved
            else:
                return cwd / path


def _bookmarks(nvim: Nvim) -> Mapping[PurePath, AbstractSet[str]]:
    acc: MutableMapping[PurePath, MutableSet[str]] = {}

    if nvim.funcs.has("nvim-0.6"):
        cwd = get_cwd(nvim)
        for mark_id in ascii_uppercase:
            _, _, _, path = nvim.api.get_mark(mark_id, {})
            if path:
                if resolved := _resolve(cwd, path=path):
                    for marked_path in chain((resolved,), ancestors(resolved)):
                        marks = acc.setdefault(marked_path, set())
                        marks.add(mark_id)

    return acc


def _quickfix(nvim: Nvim) -> Mapping[PurePath, int]:
    def it() -> Iterator[PurePath]:
        cwd = get_cwd(nvim)
        for q in nvim.funcs.getqflist():
            bufnr = q["bufnr"]
            filename = normcase(nvim.funcs.bufname(bufnr))
            yield cwd / filename

    filenames = tuple(it())
    parents = (ancestor for fullname in filenames for ancestor in ancestors(fullname))
    locations = Counter(chain(filenames, parents))

    return locations


def markers(nvim: Nvim) -> Markers:
    qf = _quickfix(nvim)
    bm = _bookmarks(nvim)
    markers = Markers(quick_fix=qf, bookmarks=bm)
    return markers
