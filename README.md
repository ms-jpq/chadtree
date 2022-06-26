# [CHADTree](https://ms-jpq.github.io/chadtree)

File Manager for Neovim, Better than NERDTree.

## Features Illustrated

**See full list of screen captures [here](https://github.com/ms-jpq/chadtree/tree/chad/docs/FEATURES.md)**

### I like speed

- **Parallel** Filesystem Scan

- **[React Like](https://reactjs.org/docs/reconciliation.html)** Reconciling Difference Minimizing Rendering engine

- **Never** blocks

_You can read more about my [performance optimization](https://github.com/ms-jpq/chadtree/tree/chad/docs/ARCHITECTURE.md) here._

### I like power

- Visual mode selections

- Create, Copy, Paste, Delete, Rename, gotta do them all

- Quickfix integration

- [Bookmarks](https://raw.githubusercontent.com/ms-jpq/chadtree/chad/docs/img/bookmarks.png)

![visual_select.gif](https://raw.githubusercontent.com/ms-jpq/chadtree/chad/docs/img/visual_select.gif)

### I like 21st century

- Filtering by glob

- Follow mode

- Session support (save open folders to disk, pick up where you left off)

- Trash support (requires [`trash`](https://formulae.brew.sh/formula/trash) or [`trash-cli`](https://github.com/andreafrancia/trash-cli))

- `ls -l` statistics

- Correct! handling of symlinks

![filtering.gif](https://raw.githubusercontent.com/ms-jpq/chadtree/chad/docs/img/filtering.gif)

### I like version control

- Asynchronous parse git status (untracked, modified, staged)

- Full support for git submodules

![git.gif](https://raw.githubusercontent.com/ms-jpq/chadtree/chad/docs/img/git_showcase.gif)

### I like colours

- Full `$LS_COLOR` support! (shows same colours as unix `ls` & `tree` commands)

- [Github coloured](https://github.com/github/linguist) icons (over 600 colours!)

- Three different sets of icons out of the box

- Four built-in themes - nord, solarized, trapdoor, vim-syntax

![ls_colours.png](https://raw.githubusercontent.com/ms-jpq/chadtree/chad/docs/img/ls_colours.png)

![github_colours.png](https://raw.githubusercontent.com/ms-jpq/chadtree/chad/docs/img/github_colours.png)

### I like refinement

- Maintain cursor position on relevant files even when during movements.

- Maintain selection when copying, moving files

- Mimetype warning (so you don't accidentally open an image)

- Validating config parser **(notice, I added an extra `"dog"` param)**

![mime warn.png](https://github.com/ms-jpq/chadtree/raw/chad/docs/img/mimetype.png)

![schema error.png](https://github.com/ms-jpq/chadtree/raw/chad/docs/img/schema_error.png)

### I like documentation

- Build-in help command in a floating window!

- Over 1000 lines of meticulous docs covering every option / function!

**Use `:CHADhelp` to view [documentation](https://github.com/ms-jpq/chadtree/tree/chad/docs)**

**Use `:CHADhelp --web` to open documentation in your browser!** (If you have one installed)

## Install

**Minimum version**: `python`: `3.8.2`, `nvim`: `0.4.3`, make sure to have `virtualenv` installed (e.g.: `sudo apt install --yes -- python3-venv`)

Install the usual way, ie.

[VimPlug](https://github.com/junegunn/vim-plug)
```vim
Plug 'ms-jpq/chadtree', {'branch': 'chad', 'do': 'python3 -m chadtree deps'}
Plug 'ms-jpq/chadtree', {'branch': 'chad', 'do': 'python3 -m chadtree deps', 'do': ':CHADdeps'}
```

You will have to run `:CHADdeps` when installing / updating. This will install CHADTree's dependencies locally inside `chadtree/.vars/runtime`.
[Packer](https://github.com/wbthomason/packer.nvim)
```vim
{ "ms-jpq/chadtree", { branch = 'chad', run = 'python3 -m chadtree deps', cmd = 'CHADdeps' }}
```

The `CHADdeps` command is run to install all of CHADTree's dependencies locallyinside `chadtree/.vars/runtime`.
You can also remove the hook from the install command and run it yourself.

Doing `rm -rf chadtree/` will cleanly remove everything CHADTree uses on your computer.

[Vundle](https://github.com/VundleVim/Vundle.vim) doesn't support installing from custom branches or hooking post commands.
If you want to install CHADTree using Vundle, you need to clone it to some directory:
```bash
git clone https://github.com/ms-jpq/chadtree --depth 1
```
"pin" it like so:
```vim
Plugin 'file://path/to/chadtree, { 'pinned': 1 }
```
And then run `:CHADdeps` manually.

## Usage

To toggle CHADTree run command `:CHADopen`. Set it to a hotkey for convenience.

```vimL
nnoremap <leader>v <cmd>CHADopen<cr>
```

To see a list of hot keys:

Either use `:CHADhelp keybind` or open in browser using [`:CHADhelp keybind --web`](https://github.com/ms-jpq/chadtree/tree/chad/docs/KEYBIND.md)

### Recommendations

Add a hotkey to clear quickfix list:

```vimL
nnoremap <leader>l <cmd>call setqflist([])<cr>
```

## If you like this...

Also check out

- [`sad`](https://github.com/ms-jpq/sad), its a modern `sed` that does previews with syntax highlighting, and lets you pick and choose which chunks to edit.

- [`coq.nvim`](https://github.com/ms-jpq/coq_nvim), it's a FAST AS FUCK completion client with shit tons of features.

- [isomorphic-copy](https://github.com/ms-jpq/isomorphic-copy), it's a cross platform clipboard that is daemonless, and does not require third party support.

## Special Thanks

CHADTree does not define it's own colours beyond some minimal defaults, all themes are imported from other open source projects.

> The base icons are imported from the [vim-devicon](https://github.com/ryanoasis/vim-devicons)

> All emoji icons are imported from the [vim-emoji-icon-theme](https://github.com/adelarsq/vim-emoji-icon-theme)

> Some themes are imported from [dircolors-solarized](https://github.com/seebi/dircolors-solarized)

> Some themes are imported from [nord-dircolors](https://github.com/arcticicestudio/nord-dircolors)

> Some themes are imported from [LS_COLORS](https://github.com/trapd00r/LS_COLORS)

> Some themes are imported from [vim-nerdtree-syntax-highlight](https://github.com/tiagofumo/vim-nerdtree-syntax-highlight)
