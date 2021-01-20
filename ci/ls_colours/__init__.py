from pathlib import Path

from ..run import docker_run

_DOCKERFILE = Path(__file__).resolve().parent / "Dockerfile"


def load_ls_colours() -> None:
    a = docker_run(_DOCKERFILE)
    print(a)
