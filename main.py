#!/usr/bin/env python3

from argparse import ArgumentParser, Namespace



def parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("--socket", default=None)
    return parser.parse_args()
