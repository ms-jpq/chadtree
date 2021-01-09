
@rpc(blocking=False, name="CHADnew")
def c_new(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    new file / folder
    """

    node = _index(nvim, state=state) or state.root
    parent = node.path if is_dir(node) else dirname(node.path)

    child: Optional[str] = nvim.funcs.input(LANG("pencil"))

    if child:
        path = join(parent, child)
        if fs_exists(path):
            s_write(nvim, LANG("already_exists", name=path), error=True)
            return Stage(state)
        else:
            try:
                new(path)
            except Exception as e:
                s_write(nvim, e, error=True)
                return _refresh(nvim, state=state, settings=settings)
            else:
                paths = frozenset(ancestors(path))
                index = state.index | paths
                new_state = forward(state, settings=settings, index=index, paths=paths)
                nxt = _open_file(
                    nvim,
                    state=new_state,
                    settings=settings,
                    path=path,
                    click_type=ClickType.secondary,
                )
                return nxt
    else:
        return None
