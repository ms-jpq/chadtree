# Keybinds

Keybinds can be customized under `chadtree_settings.keymap.<key>` with a set of keys.

---

## Window management

##### `chadtree_settings.keymap.quit`

Close CHADTree window, quit if it is the last window.

**default:**

```json
["q"]
```

##### `chadtree_settings.keymap.bigger`

Resize CHADTree window bigger.

**default:**

```json
["+", "="]
```

##### `chadtree_settings.keymap.smaller`

Resize CHADTree window smaller.

**default:**

```json
["-", "_"]
```

##### `chadtree_settings.keymap.refresh`

Refresh CHADTree.

**default:**

```json
["<c-r>"]
```

---

## Rerooting CHADTree

##### `chadtree_settings.keymap.change_dir`

Change vim's working directory.

**default:**

```json
["b"]
```

##### `chadtree_settings.keymap.change_focus`

Set CHADTree's root to folder at cursor. Does not change working directory.

**default:**

```json
["c"]
```

##### `chadtree_settings.keymap.change_focus_up`

Set CHADTree's root one level up.

**default:**

```json
["C"]
```

---

## Open file / folder

Any of the keys that open files will double as a open / close toggle on folders.

##### `chadtree_settings.keymap.primary`

Open file at cursor.

**default:**

```json
["<enter>"]
```

##### `chadtree_settings.keymap.secondary`

Open file at cursor, keep cursor in CHADTree's window.

**default:**

```json
["<tab>", "<2-leftmouse>"]
```

##### `chadtree_settings.keymap.tertiary`

Open file at cursor in a new tab.

**default:**

```json
["<m-enter>", "<middlemouse>"]
```

##### `chadtree_settings.keymap.v_split`

Open file at cursor in vertical split.

**default:**

```json
["w"]
```

##### `chadtree_settings.keymap.h_split`

Open file at cursor in horizontal split.

**default:**

```json
["W"]
```

##### `chadtree_settings.keymap.open_sys`

Open file with GUI tools using `open` or `xdg open`. This will open third party tools such as `Finder` or `KDE Dolphin` or `GNOME nautilus`, etc. Depends on platform and user setup.

**default:**

```json
["o"]
```

##### `chadtree_settings.keymap.collapse`

Collapse all subdirectories for directory at cursor.

**default:**

```json
["<s-tab>", "`"]
```

---

## Doing things with cursor

##### `chadtree_settings.keymap.refocus`

Put cursor at the root of CHADTree

**default:**

```json
["~"]
```

##### `chadtree_settings.keymap.jump_to_current`

Position cursor in CHADTree at currently open buffer, if the buffer points to a location visible under CHADTree.

**default:**

```json
["J"]
```

##### `chadtree_settings.keymap.stat`

Print `ls --long` stat for file under cursor.

**default:**

```json
["K"]
```

##### `chadtree_settings.keymap.copy_name`

Copy paths of files under cursor or visual block.

**default:**

```json
["y"]
```

##### `chadtree_settings.keymap.copy_basename`

Copy names of files under cursor or visual block.

**default:**

```json
["Y"]
```

##### `chadtree_settings.keymap.copy_relname`

Copy relative paths of files under cursor or visual block.

**default:**

```json
["<c-y>"]
```

---

## Filtering

##### `chadtree_settings.keymap.filter`

Set a glob pattern to narrow down visible files.

**default:**

```json
["f"]
```

##### `chadtree_settings.keymap.clear_filter`

Clear filter.

**default:**

```json
["F"]
```

---

## Bookmarks

##### `chadtree_settings.keymap.bookmark_goto`

Goto bookmark [1-9].

**default:**

```json
["m"]
```

##### `chadtree_settings.keymap.bookmark_set`

Set bookmark [1-9].

**default:**

```json
["M"]
```

---

## Selecting

##### `chadtree_settings.keymap.select`

Select files under cursor or visual block.

**default:**

```json
["s"]
```

##### `chadtree_settings.keymap.clear_selection`

Clear selection.

**default:**

```json
["S"]
```

---

## File operations

##### `chadtree_settings.keymap.new`

Create new file at location under cursor. Files ending with platform specific path separator will be folders.

Intermediary folders are created automatically.

ie. `uwu/owo/` under `unix` will create `uwu/` then `owo/` under it. Both are folders.

**default:**

```json
["a"]
```

##### `chadtree_settings.keymap.link`

Create links at location under cursor from selection.

Links are always relative.

Intermediary folders are created automatically.

**default:**

```json
["A"]
```

##### `chadtree_settings.keymap.rename`

Rename file under cursor.

**default:**

```json
["r"]
```

##### `chadtree_settings.keymap.toggle_exec`

Toggle all the `+x` bits of the selected / highlighted files.

Except for directories, where `-x` will prevent reading.

**default:**

```json
["X"]
```

##### `chadtree_settings.keymap.copy`

Copy the selected files to location under cursor.

**default:**

```json
["p"]
```

##### `chadtree_settings.keymap.cut`

Move the selected files to location under cursor.

**default:**

```json
["x"]
```

##### `chadtree_settings.keymap.delete`

Delete the selected files. Items deleted cannot be recovered.

**default:**

```json
["d"]
```

##### `chadtree_settings.keymap.trash`

Trash the selected files using platform specific `trash` command, if they are available. Items trashed may be recovered.

You need [`brew install trash`](https://formulae.brew.sh/formula/trash) for MacOS and [`pip3 install trash-cli`](https://github.com/andreafrancia/trash-cli) on Linux.

**default:**

```json
["t"]
```

---

## Toggle settings on / off

##### `chadtree_settings.keymap.toggle_hidden`

Toggle `show_hidden` on and off. See `chadtree_settings.options.show_hidden` for details.

**default:**

```json
["."]
```

##### `chadtree_settings.keymap.toggle_follow`

Toggle `follow` on and off. See `chadtree_settings.options.follow` for details.

**default:**

```json
["u"]
```

##### `chadtree_settings.keymap.toggle_version_control`

Toggle version control integration on and off

**default:**

```json
["i"]
```
