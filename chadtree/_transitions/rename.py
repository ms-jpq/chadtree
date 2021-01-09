
@rpc(blocking=False, name="CHADrename")
def c_rename(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    rename file / folder
    """

    node = _index(nvim, state=state)
    if node:
        prev_name = node.path
        parent = state.root.path
        rel_path = relpath(prev_name, start=parent)

        child: Optional[str] = nvim.funcs.input(LANG("pencil"), rel_path)
        if child:
            new_name = join(parent, child)
            new_parent = dirname(new_name)
            if fs_exists(new_name):
                s_write(nvim, LANG("already_exists", name=new_name), error=True)
                return Stage(state)
            else:
                try:
                    rename(prev_name, new_name)
                except Exception as e:
                    s_write(nvim, e, error=True)
                    return _refresh(nvim, state=state, settings=settings)
                else:
                    paths = frozenset((parent, new_parent, *ancestors(new_parent)))
                    index = state.index | paths
                    new_state = forward(
                        state, settings=settings, index=index, paths=paths
                    )
                    kill_buffers(nvim, paths=(prev_name,))
                    return Stage(new_state)
        else:
            return None
    else:
        return None
