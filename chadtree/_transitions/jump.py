
@rpc(blocking=False, name="CHADjump_to_current")
def c_jump_to_current(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    Jump to active file
    """

    current = state.current
    if current:
        stage = _current(nvim, state=state, settings=settings, current=current)
        if stage:
            return Stage(state=stage.state, focus=current)
        else:
            return None
    else:
        return None
