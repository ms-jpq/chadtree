# Fast FM (Work in progress)

The **BEST** file manager for Neovim

## Features

### Fast & asynchronous where it counts, (and doesn't)

- Incremental file system scan

- Async all the time. in fact, I went overboard! Literally everything is async.

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

- Globbing

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
