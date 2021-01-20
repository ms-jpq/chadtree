from json import dump

from chad_types import ARTIFACT, Artifact
from std2.pickle import encode
from std2.tree import recur_sort

from .icon_colours import load_icon_colours
from .ls_colours import load_ls_colours
from .text_decorations import load_text_decors


def main() -> None:
    icon_colours = load_icon_colours()
    icons, text_colours = load_text_decors()
    artifact = Artifact(
        icons=icons, icon_colours=icon_colours, text_colours=text_colours
    )

    json = recur_sort(encode(artifact))
    with ARTIFACT.open("w") as fd:
        dump(json, fd, ensure_ascii=False, check_circular=False, indent=2)


# main()
load_ls_colours()
