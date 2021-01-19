# [CHADTree](https://ms-jpq.github.io/chadtree)

File Manager for Neovim, Better than NERDTree.

## Features Illustrated

**See full list of screen captures [here](https://github.com/ms-jpq/chadtree/tree/future2/docs/FEATURES.md)**

### I like speed

- **Parallel** Filesystem Scan

- **Virtual Rendering** engine (React Like)

- **Never** blocks

*You can read more about my [performance optimization](https://github.com/ms-jpq/chadtree/tree/future2/docs/ARCHITECTURE.md) here.*

### I like power

- Visual mode selections

- Create, Copy, Paste, Delete, Rename, gotta do them all

- Quickfix integration

![visual_select.gif](https://raw.githubusercontent.com/ms-jpq/chadtree/future2/docs/img/visual_select.gif)

### I like 21st century

- Filtering by glob

- Follow mode

- Session support (save open folders to disk, pick up where you left off)

- Trash support (requires [`trash`](https://formulae.brew.sh/formula/trash) or [`trash-cli`](https://github.com/andreafrancia/trash-cli))

- `ls -l` statistics

- Correct! handling of symlinks

![filtering.gif](https://raw.githubusercontent.com/ms-jpq/chadtree/future2/docs/img/filtering.gif)

### I like version control

- Asynchronous parse git status (untracked, modified, staged)

- Full support for git submodules

![git.gif](https://raw.githubusercontent.com/ms-jpq/chadtree/future2/docs/img/git_showcase.gif)

### I like colours

- Full `$LS_COLOR` support! (shows same colours as unix `ls` & `tree` commands)

- [Github coloured](https://github.com/github/linguist) icons (over 600 colours!)

- Full icon support from importing [vim-devicon](https://github.com/ryanoasis/vim-devicons)

![ls_colours.png](https://raw.githubusercontent.com/ms-jpq/chadtree/future2/docs/img/ls_colours.png)

![github_colours.png](https://raw.githubusercontent.com/ms-jpq/chadtree/future2/docs/img/github_colours.png)

### I like refinement

- Automatically move cursor to new file upon creation / renaming

- Maintain selection when copying, moving files

- Mimetype warning (so you don't accidently open an image)

- Vaildating config parser (notice, I added an extra `dog` param)

![mime warn.png](https://github.com/ms-jpq/chadtree/raw/future2/docs/img/mimetype.png)

![schema error.png](https://github.com/ms-jpq/chadtree/raw/future2/docs/img/schema_error.png)

## Install

**Minimum version**: `python`: 3.8.2, `nvim`: `0.4.3`

Install the usual way, ie. [VimPlug](https://github.com/junegunn/vim-plug), [Vundle](https://github.com/VundleVim/Vundle.vim), etc

```VimL
Plug 'ms-jpq/chadtree', {'branch': 'chad', 'do': 'python3 -m chadtree deps'}
```

You will have to run `:CHADdeps` when installing / updating. This will install CHADTree's depdencies locally inside `chadtree/.vars/runtime`.

doing `rm -rf chadtree/` will cleanly remove everything CHADTree uses on your computer.

## Documentation

To toggle CHADTree run command `:CHADopen`. Set it to a hotkey for convenience.

```vimL
nnoremap <leader>v <cmd>CHADopen<cr>
```

Use `:CHADhelp` to view [documentation](https://github.com/ms-jpq/chadtree/tree/future2/docs)

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
