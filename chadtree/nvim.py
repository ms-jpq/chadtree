from pynvim import Nvim


def getcwd(nvim: Nvim) -> str:
    cwd: str = nvim.funcs.getcwd()
    return cwd
