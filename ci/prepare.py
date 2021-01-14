#!/usr/bin/env python3

from os import environ, getcwd
from os.path import isdir
from pathlib import Path
from subprocess import run

_TOP_LV = Path(__file__).resolve().parent.parent


def call(prog: str, *args: str, cwd: str = getcwd()) -> None:
    ret = run((prog, *args), cwd=cwd)
    if ret.returncode != 0:
        exit(ret.returncode)


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
        call("git", "clone", "--branch", branch, uri, name)
        call("git", "config", "user.email", email, cwd=name)
        call("git", "config", "user.name", username, cwd=name)


def build(cwd: str) -> None:
    script = str(_TOP_LV / "ci" / "build.py")
    call(script, cwd=cwd)


def main() -> None:
    cwd = "temp"
    git_clone(cwd)
    build(cwd)


main()
