# Fast FM (100% async)

Work in progress

The **BEST** file manager for Neovim

## Features

### Fast & asynchronous where it counts, (and doesn't), either way, it's async all the time

- Incremental file system scan

- Literally every API call is async.

- Literally every FS call is async.

### Integrated git support

- Asynchronous parse git status (untracked, modified, staged)

- Full support for git ignore, toggle show / hide

### Attention to detail

- Visual mode multi select

- Always reuse-buffers, open files in correct windows, auto kill stale buffers

- Shows symlinks

### Unique features

- Follow mode

- Session support

- Full globbing support

## Preview

## Install

Requires pyvim (as all python plugins do)

```sh
pip3 install pynvim
```

Install the usual way, ie. [VimPlug](https://github.com/junegunn/vim-plug), [Vundle](https://github.com/VundleVim/Vundle.vim), etc

```VimL
Plug 'ms-jpq/fast-fm', {'branch': 'nvim', 'do': ':UpdateRemotePlugins'}
```

## Documentation
