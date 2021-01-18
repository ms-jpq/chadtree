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

## Validation

Variables will be validated against a schema.

ie.

```vim
let g:chadtree_settings = { 'ignore.dog': 'scratch, stratch' }
```

Will give you the following error message:

![schema error.png](https://raw.githubusercontent.com/ms-jpq/chadtree/chad/preview/schema_error.png)

### Specifics

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

### `chadtree_settings.ignore`
