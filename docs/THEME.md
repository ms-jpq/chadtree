# Theme

CHADTree does not define it's own theme, outside of some minimal defaults.

All themes are imported from other open source projects.

## Colours

### Highlight Group

Vim comes with some built-in highlight groups, these are used to colour things which I cannot find good imports for.

You can define them at `chadtree_settings.view.highlights`.

see `:help highlight-groups`

### LS_COLORS

On `unix`, the command `ls` can produce coloured results based on the `LS_COLORS` environmental variable.

CHADTree can pretend it's `ls` by setting `chadtree_settings.view.colours` to `ls_colours`.

#### Sources

If you do not like whatever `LS_COLORS` came with your machine, or perhaps you don't even have one.

There are lots of options online, see:

[dircolors-solarized](https://github.com/seebi/dircolors-solarized)

[nord-dircolors](https://github.com/arcticicestudio/nord-dircolors)

[LS_COLORS](https://github.com/trapd00r/LS_COLORS)

### NerdTree Colours

If none of the `LS_COLORS` interest you. You can use the colours from [vim-nerdtree-syntax-highlight](https://github.com/tiagofumo/vim-nerdtree-syntax-highlight).

Just set `chadtree_settings.view.colours` to `nerd_tree`.

Note, under `background=light` the original colours are inversed, because nobody wants `#FFFFFF` primiary text on a light background.

### Github Colours

This one is for the icons only. They are coloured according to [Github linguist](https://github.com/github/linguist).

## Icons

There are three options to `chadtree_settings.view.icon_set`:

**devicons:**

Imported from [vim-devicons](https://github.com/ryanoasis/vim-devicons)

![devicons.png](https://github.com/ms-jpq/chadtree/raw/future2/docs/img/icons_devicons.png)

**emoji:**

Imported from [vim-emoji-icon-theme](https://github.com/adelarsq/vim-emoji-icon-theme)

![emojicons.png](https://github.com/ms-jpq/chadtree/raw/future2/docs/img/icons_emoji.png)

**ascii:**

![asciicons.png](https://github.com/ms-jpq/chadtree/raw/future2/docs/img/icons_ascii.png)