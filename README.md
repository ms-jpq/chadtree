# CHADTree

Async File Manager for Neovim, Better than NERDTree.

## Features Illustrated

**See full list of screen captures [here](https://github.com/ms-jpq/chadtree/tree/chad/preview)**

### I like speed

- Incremental file system scan

- None blocking

- Literally every FS call is async.

### I like power

- Visual mode selections

- Create, Copy, Paste, Delete, Rename, gotta do them all

- Quickfix integration

![visual_select.gif](https://raw.githubusercontent.com/ms-jpq/chadtree/chad/preview/visual_select.gif)

### I like 21st century

- Filtering by glob

- Follow mode

- Session support (save open folders to disk, pick up where you left off)

![filtering.gif](https://raw.githubusercontent.com/ms-jpq/chadtree/chad/preview/filtering.gif)

### I like version control

- Asynchronous parse git status (untracked, modified, staged)

* Full support for git ignore, toggle show / hide

* Full support for globbing ignored files

![git.gif](https://raw.githubusercontent.com/ms-jpq/chadtree/chad/preview/git.gif)

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

Minimum version: `python`: 3.7, `nvim`: `0.4.3`

## Documentation

To toggle CHADTree run command `:CHADopen`. Set it to a hotkey for convenience.

```vimL
nnoremap <leader>v <cmd>CHADopen<cr>
```

Check out [config.json](https://github.com/ms-jpq/chadtree/blob/chad/config/config.json) before you proceed for an overview of options.

Set a dictionary with same keys to `g:chadtree_settings` to overwrite any options. You dont need to provide every key, just the ones you want to overwrite.

### Keybindings

`functions` only work under the CHADTree buffer

| functions     | usage                                                               | default key     |
| ------------- | ------------------------------------------------------------------- | --------------- |
| quit          | close chad window                                                   | `q`             |
| refresh       | trigger refresh                                                     | `<c-r>`         |
| primary       | open / close folders & open file                                    | `<enter>`       |
| secondary     | open / close folders & preview file                                 | `<tab>`         |
| open_sys      | open file using `open` / `xdg-open`                                 | `o`             |
| toggle_hidden | toggle showing hidden items                                         | `.`             |
| collapse      | collapse all sub folders                                            | `<s-tab>`, `\\` |
| copy_name     | copy file path of items under cursor / visual selection / selection | `y`             |
| filter        | set glob filter for visible items                                   | `f`             |
| clear_filter  | clear filtering                                                     | `F`             |
| select        | select item under cursor / visual selection                         | `s`             |
| clear_select  | clear selection                                                     | `c`             |
| new           | create new file at location under cursor                            | `a`             |
| rename        | rename file under cursor                                            | `r`             |
| delete        | delete item under cursor / visual selection / selection             | `d`             |
| copy          | copy selected items to location under cursor                        | `p`             |
| cut           | move selected items to location under cursor                        | `x`             |
| toggle_follow | toggle follow mode on / off                                         |                 |
| bigger        | increase chad size                                                  | `+`, `=`        |
| smaller       | decrease chad size                                                  | `-`, `_`        |

### View & Ignore

Likewise set dictionaries to `g:chadtree_view` and `g:chadtree_ignores` to overwrite [view.json](https://github.com/ms-jpq/chadtree/blob/chad/config/view.json) and [ignore.json](https://github.com/ms-jpq/chadtree/blob/chad/config/ignore.json) accordingly.

| option | usage                       |
| ------ | --------------------------- |
| name   | globs of name to ignore     |
| path   | glob of full path to ignore |

## Special Thanks

All the Icons are imported from the [vim-devicon]() project
