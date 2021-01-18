# Configurations

All configurations are under the global variable `chadtree_settings`.

VimL:

```vim
let g:chadtree_settings = { ... }
```

Lua:

```lua
local chad_settings = { ... }
vim.api.nvim_set_var("chadtree_settings", chad_settings)
```

---

## Shorthand

Dictionary keys will be automatically expanded with the `.` notation. This works recursively.

ie. The following are equivalent

```json
{ "dog.puppy": 2 }
```

```json
{ "dog": { "puppy": 2 } }
```

Note in lua, you will need to quote your keys like so:

```lua
{ ["dog.puppy"] = 2 }
```

---

## Validation

Variables will be validated against a schema.

ie.

```vim
let g:chadtree_settings = { 'ignore.dog': 'scratch, stratch' }
```

Will give you the following error message:

![schema error.png](https://raw.githubusercontent.com/ms-jpq/chadtree/chad/preview/schema_error.png)

---

## Specifics

The default configuration can be found under an [`yaml` file](https://github.com/ms-jpq/chadtree/blob/chad/config/defaults.yml)

### `chadtree_settings.options`

#### `chadtree_settings.options.follow`

CHADTree will highlight currently open file.

**default:**

```json
true
```

#### `chadtree_settings.options.lang`

CHADTree will guess your locale from [unix environmental variables](https://pubs.opengroup.org/onlinepubs/7908799/xbd/envvar.html).

Set to `c` to disable emojis.

**default:**

```json
null
```

**note:**

I only wrote localization for `en`. `zh` will be coming, and maybe `fr` if I can get my girlfriend to help.

#### `chadtree_settings.options.mimetypes`

CHADTree will attempt to warn you when you try to open say an image. This is done via the [Internet Assigned Numbers Authority](https://www.iana.org/assignments/media-types/media-types.xhtml)'s mimetype database.

##### `chadtree_settings.options.mimetypes.warn`

Show a warning before opening these datatypes

**default:**

```json
["audio", "font", "image", "video"]
```

##### `chadtree_settings.options.mimetypes.allow_exts`

Skip warning for these extensions

**default:**

```json
[".ts"]
```

#### `chadtree_settings.options.page_increment`

Change how many lines `{` and `}` scroll

**default:**

```json
5
```

#### `chadtree_settings.options.polling_rate`

CHADTree's background refresh rate

**default:**

```json
2.0
```

#### `chadtree_settings.options.session`

Save & restore currently open folders

**default:**

```json
true
```

#### `chadtree_settings.options.show_hidden`

Hide some files and folders by default. By default this can be toggled using the `.` key.

see `chadtree_settings.ignore` for more details

**default:**

```json
false
```

#### `chadtree_settings.options.version_control`

##### `chadtree_settings.options.version_control.enable`

Enable version control. This can also be toggled. But unlike `show_hidden`, does not have a default keybind.

**default:**

```json
true
```

### `chadtree_settings.ignore`

CHADTree can ignore showing some files. This is toggable by default using the `.` key.

#### `chadtree_settings.ignore.name_exact`

Files whose name match these exactly will be ignored.

**default:**

```json
[".DS_Store", ".directory", "thumbs.db", ".git"]
```

#### `chadtree_settings.ignore.name_glob`

Files whose name match these [glob patterns](https://en.wikipedia.org/wiki/Glob_%28programming%29) will be ignored.

ie. `*.py` will match all python files

**default:**

```json
[]
```

#### `chadtree_settings.ignore.path_glob`

Files whose full path match these [glob patterns](https://en.wikipedia.org/wiki/Glob_%28programming%29) will be ignored.

**default:**

```json
[]
```

### `chadtree_settings.view`

#### `chadtree_settings.view.colours`

#### `chadtree_settings.view.highlights`

#### `chadtree_settings.view.open_direction`

#### `chadtree_settings.view.sort_by`

#### `chadtree_settings.view.time_format`

#### `chadtree_settings.view.use_icons`

#### `chadtree_settings.view.width`

#### `chadtree_settings.view.window_options`
