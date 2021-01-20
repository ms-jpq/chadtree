from json import loads
from pathlib import Path

from chad_types import LSColourSet
from std2.pickle import decode

from ..run import docker_run

_DOCKERFILE = Path(__file__).resolve().parent / "Dockerfile"


def load_ls_colours() -> LSColourSet:
    json = loads(docker_run(_DOCKERFILE))
    lsc: LSColourSet = decode(LSColourSet, json)
    return lsc
