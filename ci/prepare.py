#!/usr/bin/env python3

from datetime import datetime
from os import environ
from os.path import isdir
from pathlib import Path
from subprocess import check_call, check_output, run
from typing import Iterator

_TOP_LV = Path(__file__).resolve().parent.parent


def _get_branch() -> str:
    ref = environ["GITHUB_REF"]
    return ref.replace("refs/heads/", "")


def _git_clone(name: str) -> None:
    if not isdir(name):
        token = environ["CI_TOKEN"]
        uri = f"https://ms-jpq:{token}@github.com/ms-jpq/chadtree.git"
        email = "ci@ci.ci"
        username = "ci-bot"
        branch = _get_branch()
        check_call(("git", "clone", "--branch", branch, uri, name))
        check_call(("git", "config", "user.email", email), cwd=name)
        check_call(("git", "config", "user.name", username), cwd=name)


def _build() -> None:
    check_call(("python3", "-m", "ci"), cwd=_TOP_LV)


def _git_alert(cwd: str) -> None:
    prefix = "update-icons"
    remote_brs = check_output(("git", "branch", "--remotes"), text=True, cwd=cwd)

    def cont() -> Iterator[str]:
        for br in remote_brs.splitlines():
            b = br.strip()
            if b and "->" not in b:
                _, _, name = b.partition("/")
                if name.startswith(prefix):
                    yield name

    refs = tuple(cont())

    if refs:
        check_call(("git", "push", "--delete", "origin", *refs), cwd=cwd)

    proc = run(("git", "diff", "--exit-code"))
    if proc.returncode:
        time = datetime.now().strftime("%Y-%m-%d")
        brname = f"{prefix}--{time}"
        check_call(("git", "checkout", "-b", brname))
        check_call(("git", "add", "."))
        check_call(("git", "commit", "-m", f"update_icons: {time}"))
        check_call(("git", "push", "--set-upstream", "origin", brname))


def main() -> None:
    cwd = "temp"
    _git_clone(cwd)
    _build()
    _git_alert(cwd)


main()
