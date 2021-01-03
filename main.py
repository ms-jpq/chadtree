#!/usr/bin/env python3

# from argparse import ArgumentParser, Namespace

# from pynvim import attach
# from pynvim_pp.client import run_client
# from chadtree.client import Client


# def parse_args() -> Namespace:
#     parser = ArgumentParser()
#     parser.add_argument("socket")
#     return parser.parse_args()


# def main() -> None:
#     args = parse_args()
#     nvim = attach("socket", path=args.socket)
#     code = run_client(nvim, client=Client())
#     exit(code)


# main()