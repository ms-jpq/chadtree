from json import loads
from pathlib import Path

from std2.pickle import new_decoder

from chad_types import LSColourSet

from ..run import docker_run

_DOCKERFILE = Path(__file__).resolve().parent / "Dockerfile"


def load_ls_colours() -> LSColourSet:
    decode = new_decoder[LSColourSet](LSColourSet)

    json = loads(docker_run(_DOCKERFILE))
    lsc = decode(json)
    return lsc
