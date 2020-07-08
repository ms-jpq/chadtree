from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Tree:
    name: str


def tree() -> Tree:
    return Tree(name="LOL")
