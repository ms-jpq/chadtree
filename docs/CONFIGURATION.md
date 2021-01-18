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
{"dog.puppy": 2}
```

```json
{"dog": {"puppy": 2}}
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

default:

```json
true
```

#### `chadtree_settings.options.lang`

default:
```json
null
```

### `chadtree_settings.ignore`