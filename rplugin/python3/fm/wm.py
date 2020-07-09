from pynvim import Nvim


def toggle(nvim: Nvim) -> None:
    tab = nvim.api.get_current_tabpage()
    windows = nvim.api.tabpage_list_wins(tab)
    buffers = tuple(nvim.api.win_get_buf(w) for w in windows)

    for b in buffers:
        ft = nvim.api.buf_get_option(b, "filetype")
        nvim.out_write(ft + "\n")
