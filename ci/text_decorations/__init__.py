from pathlib import Path
from ..run import docker_run

_DOCKERFILE = Path(__file__).resolve().parent / "Dockerfile"


def load_text_decors() -> str:
    aaa = docker_run(_DOCKERFILE)
    print(aaa)
