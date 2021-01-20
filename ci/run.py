from pathlib import Path
from subprocess import check_call, check_output


def docker_run(dockerfile: Path) -> str:
    parent = dockerfile.parent
    print(parent)
    name = f"chad_{parent.name}"
    check_call(("docker", "build", "-t", name, "-f", "Dockerfile", "."), cwd=parent)
    output = check_output(("docker", "run", "--rm", name))
    return output
