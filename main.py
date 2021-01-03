#!/usr/bin/env python3

from sys import version_info, stderr

if version_info < (3, 8, 2):
    msg = "For python < 3.8.2 please install using the branch -- legacy"
    print(msg, file=stderr)
    exit(1)


from argparse import ArgumentParser, Namespace

from pynvim import attach
from pynvim_pp.client import run_client
from chadtree.client import ChadClient


def parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("socket")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    nvim = attach("socket", path=args.socket)
    code = run_client(nvim, client=ChadClient())
    exit(code)


main()