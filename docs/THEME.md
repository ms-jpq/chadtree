# Theme

CHADTree does not define it's own theme, outside of some minimal defaults.

All themes are imported from other open source projects.

You can customize themes using the `chadtree_settings.theme` settings.

---

### `chadtree_settings.theme.highlights`

Vim comes with some built-in highlight groups, these are used to colour things which I cannot find good imports for.

see `:help highlight-groups`

#### `chadtree_settings.theme.highlights.ignored`

These are used for files that are ignored by user supplied pattern in `chadtree_settings.ignore` and by version control.

**default:**

```json
"Comment"
```

#### `chadtree_settings.theme.highlights.bookmarks`

These are used to show bookmarks.

**default:**

```json
"Title"
```

#### `chadtree_settings.theme.highlights.quickfix`

These are used to notify the number of times a file / folder appears in the `quickfix` list.

**default:**

```json
"Label"
```

#### `chadtree_settings.theme.highlights.version_control`

These are used to put a version control status beside each file.

**default:**

```json
"Comment"
```

---

### `chadtree_settings.theme.icon_glyph_set`

To use **devicons**, you will need [supported fonts](https://github.com/ryanoasis/nerd-fonts#font-installation)

**devicons:**

Imported from [vim-devicons](https://github.com/ryanoasis/vim-devicons)

![devicons.png](https://github.com/ms-jpq/chadtree/raw/chad/docs/img/icons_devicons.png)

**emoji:**

Imported from [vim-emoji-icon-theme](https://github.com/adelarsq/vim-emoji-icon-theme)

![emojicons.png](https://github.com/ms-jpq/chadtree/raw/chad/docs/img/icons_emoji.png)

**ascii:**

![asciicons.png](https://github.com/ms-jpq/chadtree/raw/chad/docs/img/icons_ascii.png)

**ascii_hollow:**

![ascii_hollow_icons.png](https://github.com/ms-jpq/chadtree/raw/chad/docs/img/icons_ascii_hollow.png)


**default:**

```json
"devicons"
```

---

### `chadtree_settings.theme.text_colour_set`

On `unix`, the command `ls` can produce coloured results based on the `LS_COLORS` environmental variable.

CHADTree can pretend it's `ls` by setting `chadtree_settings.theme.text_colour_set` to `env`.

If you are not happy with that, you can choose one of the many others:

- [dircolors-solarized](https://github.com/seebi/dircolors-solarized)

- [nord-dircolors](https://github.com/arcticicestudio/nord-dircolors)

- [trapd00r](https://github.com/trapd00r/LS_COLORS)

- [vim-nerdtree-syntax-highlight](https://github.com/tiagofumo/vim-nerdtree-syntax-highlight)

**legal keys: one of**

```json
[
  "env",
  "solarized_dark_256",
  "solarized_dark",
  "solarized_light",
  "solarized_universal",
  "nord",
  "trapdoor",
  "nerdtree_syntax_light",
  "nerdtree_syntax_dark"
]
```

**default:**

```json
"env"
```

---

### `chadtree_settings.theme.icon_colour_set`

Right now you all the file icons are coloured according to [Github colours](https://github.com/github/linguist).

You may also disable colouring if you wish.

**github:**

![github_colours.png](https://raw.githubusercontent.com/ms-jpq/chadtree/chad/docs/img/github_colours.png)

**legal keys: one of**

```json
["github", "none"]
```

**default:**

```json
"github"
```

---
