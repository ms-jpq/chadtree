# [CHADTree](https://ms-jpq.github.io/chadtree)

File Manager for Neovim, Better than NERDTree.

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

- Trash support (requires [`trash`](https://formulae.brew.sh/formula/trash) or [`trash-cli`](https://github.com/andreafrancia/trash-cli))

- `ls -l` statistics

- Correct! handling of symlinks

- Mimetype warning (so you don't accidently open an image)

![filtering.gif](https://raw.githubusercontent.com/ms-jpq/chadtree/chad/preview/filtering.gif)

### I like version control

- Asynchronous parse git status (untracked, modified, staged)

- Full support for git ignore, toggle show / hide

- Full support for globbing ignored files

![git.gif](https://raw.githubusercontent.com/ms-jpq/chadtree/chad/preview/git.gif)

### I like colours

- Full `$LS_COLOR` support! (shows same colours as unix `ls` & `tree` commands)

- [Github coloured](https://github.com/github/linguist) icons (over 600 colours!)

- Full icon support from importing [vim-devicon](https://github.com/ryanoasis/vim-devicons)

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

**Minimum version**: `python`: 3.7, `nvim`: `0.4.3`

## Documentation

**important:** if you get a missing function error or see a new feature here but can't use yet, it means I added a feature and you need to run `:UpdateRemotePlugins` to see the new function.

This is a Neovim limitation.

To toggle CHADTree run command `:CHADopen`. Set it to a hotkey for convenience.

```vimL
nnoremap <leader>v <cmd>CHADopen<cr>
```

Use `:CHADopen --nofocus` to open but not focus on the sidebar.

Check out [config.json](https://github.com/ms-jpq/chadtree/blob/chad/config/config.json) before you proceed for an overview of options.

Set a dictionary with same keys to `g:chadtree_settings` to overwrite any options. You dont need to provide every key, just the ones you want to overwrite.

### Keybindings

`functions` only work under the CHADTree buffer

| functions              | usage                                                                                                | default key                  |
| ---------------------- | ---------------------------------------------------------------------------------------------------- | ---------------------------- |
| quit                   | close chad window                                                                                    | `q`                          |
| refresh                | trigger refresh                                                                                      | `<c-r>`                      |
| change_focus           | re-center root at folder                                                                             | `c`                          |
| change_focus_up        | re-center root at root's parent                                                                      | `C`                          |
| refocus                | refocus root at vim cwd                                                                              | `~`                          |
| jump_to_current        | set cursor row to currently active file                                                              | `J`                          |
| primary                | open / close folders & open file                                                                     | `<enter>`                    |
| secondary              | open / close folders & preview file                                                                  | `<tab>`, `<doubleclick>`     |
| tertiary               | open / close folders & open file in new tab                                                          | `<m-enter>`, `<middlemouse>` |
| v_split                | open / close folders & open file in vertical split                                                   | `w`                          |
| h_split                | open / close folders & open file in horizontal split                                                 | `W`                          |
| open_sys               | open file using `open` / `xdg-open`                                                                  | `o`                          |
| toggle_hidden          | toggle showing hidden items _(you need to set your own ignore list)_                                 | `.`                          |
| collapse               | collapse all sub folders                                                                             | `<s-tab>`                    |
| copy_name              | copy file path of items under cursor / visual selection / selection                                  | `y`                          |
| filter                 | set glob filter for visible items                                                                    | `f`                          |
| clear_filter           | clear filtering                                                                                      | `F`                          |
| select                 | select item under cursor / visual selection                                                          | `s`                          |
| clear_select           | clear selection                                                                                      | `S`                          |
| new                    | create new folder / file at location under cursor (name ending with os specific `/` will be folders) | `a`                          |
| rename                 | rename file under cursor                                                                             | `r`                          |
| delete                 | delete item under cursor / visual selection / selection                                              | `d`                          |
| trash                  | trash item under cursor / visual selection / selection                                               | `t`                          |
| copy                   | copy selected items to location under cursor                                                         | `p`                          |
| cut                    | move selected items to location under cursor                                                         | `x`                          |
| stat                   | print `ls -l` stat to status line                                                                    | `K`                          |
| toggle_follow          | toggle follow mode on / off                                                                          |                              |
| toggle_version_control | toggle version control on / off                                                                      |
| bigger                 | increase chad size                                                                                   | `+`, `=`                     |
| smaller                | decrease chad size                                                                                   | `-`, `_`                     |

### View & Ignore

**important:** if you are not seeing Icons, you are probably missing the [correct font](https://github.com/ryanoasis/nerd-fonts).

Likewise set dictionaries to `g:chadtree_view` and `g:chadtree_ignores` to overwrite [view.json](https://github.com/ms-jpq/chadtree/blob/chad/config/view.json) and [ignore.json](https://github.com/ms-jpq/chadtree/blob/chad/config/ignore.json) accordingly.

| option | usage                       |
| ------ | --------------------------- |
| name   | globs of name to ignore     |
| path   | glob of full path to ignore |

Note: **if you want to ignore dotfiles, you will need to set it up like so**

```vimL
lua vim.api.nvim_set_var("chadtree_ignores", { name = {".*", ".git"} })
```

To use [emoji theme](https://github.com/adelarsq/vim-emoji-icon-theme)

```vimL
lua vim.api.nvim_set_var("chadtree_settings", { use_icons = "emoji" })
```

### Colours

Where to get `LS_COLORS`? Lots of places,such as [here](https://github.com/seebi/dircolors-solarized) or [here](https://github.com/trapd00r/LS_COLORS).

Set `g:chadtree_colours` to customize colour mappings for `8bit` -> `24bit` [mappings](https://github.com/ms-jpq/chadtree/blob/chad/config/colours.json).

Vaild values for `hl24` include hexcodes such as `#FFFFF`

### Recommendations

Add a hotkey to clear quickfix list:

```vimL
nnoremap <leader>l <cmd>call setqflist([])<cr>
```

## If you like this...

Also check out

- [`sad`](https://github.com/ms-jpq/sad), its a modern `sed` that does previews with syntax highlighting, and lets you pick and choose which chunks to edit.

- [isomorphic-copy](https://github.com/ms-jpq/isomorphic-copy), it's a cross platform clipboard that is daemonless, and does not require third party support.

## Special Thanks

> The base icons are imported from the [vim-devicon](https://github.com/ryanoasis/vim-devicons) project

> All emoji icons are imported from the [vim-emoji-icon-theme](https://github.com/adelarsq/vim-emoji-icon-theme) project by [adelarsq](https://github.com/adelarsq)
