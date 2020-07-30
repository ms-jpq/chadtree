# CHADTree

Async File Manager for Neovim, Better than NERDTree.

**WORK IN PROGRESS**

## Highlight

- Async everything & Incremental scan

- Batch Operations via visual mode

- Follow mode & Session support

- Git support & toggle show / hide

- Github colours & `LS_COLOR` support

## Features Illustrated

### I like speed

- Incremental file system scan

- None blocking

- Literally every FS call is async.

### I like power

- Visual mode selections

- Create, Copy, Paste, Delete, Rename, gotta do them all

- Quickfix integration

![visual_select.gif](https://raw.githubusercontent.com/ms-jpq/chadtree/chad/preview/visual_select.gif)

![quickfix.gif](https://raw.githubusercontent.com/ms-jpq/chadtree/chad/preview/quickfix.gif)

### I like 21st century

- Follow mode

- Session support (save open folders to disk, pick up where you left off)

![follow.gif](https://raw.githubusercontent.com/ms-jpq/chadtree/chad/preview/follow.gif)

### I like version control

- Asynchronous parse git status (untracked, modified, staged)

* Full support for git ignore, toggle show / hide

* Full support for globbing ignored files

![git.gif](https://raw.githubusercontent.com/ms-jpq/chadtree/chad/preview/git.gif)

![git_hide.gif](https://raw.githubusercontent.com/ms-jpq/chadtree/chad/preview/git_hide.gif)

### I like colours

- Full `$LS_COLOR` support! (shows same colours as unix `ls` & `tree` commands)

* [Github coloured](https://github.com/github/linguist) icons

![ls_colours.png](https://raw.githubusercontent.com/ms-jpq/chadtree/chad/preview/ls_colours.png)

![github_colours.png](https://raw.githubusercontent.com/ms-jpq/chadtree/chad/preview/github_colours.png)

## Install

Requires pyvim (as all python plugins do)

```sh
pip3 install pynvim
```

Install the usual way, ie. [VimPlug](https://github.com/junegunn/vim-plug), [Vundle](https://github.com/VundleVim/Vundle.vim), etc

```VimL
Plug 'ms-jpq/chadtree', {'branch': 'chad', 'do': ':UpdateRemotePlugins'}
```

## Documentation
