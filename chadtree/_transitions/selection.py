
@rpc(blocking=False, name="CHADclear_selection")
def c_clear_selection(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Stage:
    """
    Clear selected
    """

    new_state = forward(state, settings=settings, selection=frozenset())
    return Stage(new_state)




@rpc(blocking=False, name="CHADselect")
def c_select(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    Folder / File -> select
    """

    nodes = iter(_indices(nvim, state=state, is_visual=is_visual))
    if is_visual:
        selection = state.selection ^ {n.path for n in nodes}
        new_state = forward(state, settings=settings, selection=selection)
        return Stage(new_state)
    else:
        node = next(nodes, None)
        if node:
            selection = state.selection ^ {node.path}
            new_state = forward(state, settings=settings, selection=selection)
            return Stage(new_state)
        else:
            return None
