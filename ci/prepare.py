#!/usr/bin/env python3

from os import environ
from os.path import isdir
from pathlib import Path
from subprocess import check_call

_TOP_LV = Path(__file__).resolve().parent.parent


def get_branch() -> str:
    ref = environ["GITHUB_REF"]
    return ref.replace("refs/heads/", "")


def git_clone(name: str) -> None:
    if not isdir(name):
        token = environ["CI_TOKEN"]
        uri = f"https://ms-jpq:{token}@github.com/ms-jpq/chadtree.git"
        email = "ci@ci.ci"
        username = "ci-bot"
        branch = get_branch()
        check_call(("git", "clone", "--branch", branch, uri, name))
        check_call(("git", "config", "user.email", email), cwd=name)
        check_call(("git", "config", "user.name", username), cwd=name)


def build(cwd: str) -> None:
    script = str(_TOP_LV / "ci" / "build.py")
    check_call((script,), cwd=cwd)


def main() -> None:
    cwd = "temp"
    git_clone(cwd)
    build(cwd)


main()
