#!/usr/bin/env python3

from os import environ, getcwd
from os.path import isdir
from subprocess import run


def call(prog: str, *args: str, cwd: str = getcwd()) -> None:
    ret = run((prog, *args), cwd=cwd)
    if ret.returncode != 0:
        exit(ret.returncode)


def git_clone(name: str) -> None:
    if not isdir(name):
        token = environ["CI_TOKEN"]
        uri = f"https://ms-jpq:{token}@github.com/ms-jpq/chadtree.git"
        email = "ci@ci.ci"
        username = "ci-bot"
        call("git", "clone", uri, name)
        call("git", "config", "--global", "user.email", email, cwd=name)
        call("git", "config", "--global", "user.name", username, cwd=name)


def build() -> None:
    call("./temp/ci/build.py")


def main() -> None:
    git_clone("temp")
    build()


main()
