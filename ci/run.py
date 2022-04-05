from pathlib import Path
from subprocess import check_call, check_output


def docker_run(dockerfile: Path) -> str:
    parent = dockerfile.parent
    name = f"chad_{parent.name}"
    check_call(
        (
            "docker",
            "buildx",
            "--tag",
            name,
            "--file",
            dockerfile,
            "--",
            ".",
        ),
        cwd=parent,
    )
    output = check_output(("docker", "run", "--rm", name), text=True)
    return output
