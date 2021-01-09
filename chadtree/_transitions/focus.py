
@rpc(blocking=False, name="CHADchange_focus")
def c_change_focus(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    Refocus root directory
    """

    node = _index(nvim, state=state)
    if node:
        new_base = node.path if Mode.folder in node.mode else dirname(node.path)
        return _change_dir(nvim, state=state, settings=settings, new_base=new_base)
    else:
        return None


@rpc(blocking=False, name="CHADchange_focus_up")
def c_change_focus_up(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    Refocus root directory up
    """

    c_root = state.root.path
    parent = dirname(c_root)
    if parent and parent != c_root:
        return _change_dir(nvim, state=state, settings=settings, new_base=parent)
    else:
        return None