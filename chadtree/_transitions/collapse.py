
@rpc(blocking=False, name="CHADcollapse")
def c_collapse(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    Collapse folder
    """

    node = _index(nvim, state=state)
    if node:
        path = node.path if Mode.folder in node.mode else dirname(node.path)
        if path != state.root.path:
            paths = frozenset(
                i for i in state.index if i == path or is_parent(parent=path, child=i)
            )
            index = state.index - paths
            new_state = forward(state, settings=settings, index=index, paths=paths)
            row = new_state.derived.paths_lookup.get(path, 0)
            if row:
                window: Window = nvim.api.get_current_win()
                _, col = nvim.api.win_get_cursor(window)
                nvim.api.win_set_cursor(window, (row + 1, col))

            return Stage(new_state)
        else:
            return None
    else:
        return None

