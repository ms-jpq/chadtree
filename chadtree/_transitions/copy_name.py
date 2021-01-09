

@rpc(blocking=False, name="CHADcopy_name")
def c_copy_name(nvim: Nvim, state: State, settings: Settings, is_visual: bool) -> None:
    """
    Copy dirname / filename
    """

    def gen_paths() -> Iterator[str]:
        selection = state.selection
        if is_visual or not selection:
            nodes = _indices(nvim, state=state, is_visual=is_visual)
            for node in nodes:
                yield node.path
        else:
            for selected in sorted(selection, key=strxfrm):
                yield selected

    paths = tuple(path for path in gen_paths())

    clip = linesep.join(paths)
    copied_paths = ", ".join(paths)

    nvim.funcs.setreg("+", clip)
    nvim.funcs.setreg("*", clip)
    s_write(nvim, LANG("copy_paths", copied_paths=copied_paths))


