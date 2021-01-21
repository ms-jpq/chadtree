# Docs

Use `:CHADhelp` to open up a list of help pages!

Help docs are written in `markdown` because a picture is worth a thousand words.

Use `:CHADhelp -w` or `:CHADhelp --web` to open help pages in a browser window if possible.

Use `:CHADhelp {topic}` or `:CHADhelp {topic} --web` to visit a particular topic for more information

- [:CHADhelp features](https://github.com/ms-jpq/chadtree/tree/chad/docs/FEATURES.md)

- [:CHADhelp keybind](https://github.com/ms-jpq/chadtree/tree/chad/docs/KEYBIND.md)

- [:CHADhelp config](https://github.com/ms-jpq/chadtree/tree/chad/docs/CONFIGURATION.md)

- [:CHADhelp theme](https://github.com/ms-jpq/chadtree/tree/chad/docs/THEME.md)

- [:CHADhelp migration](https://github.com/ms-jpq/chadtree/tree/chad/docs/MIGRATION.md)

---

## Commands

### `CHADopen`

`:CHADopen` will toggle CHADTree open / close

`:CHADopen --nofocus` will open CHADTree without giving the sidebar focus

### `CHADdeps`

`:CHADdeps` will install all of CHADTree's depdencies locally.

Dependencies will be privately installed inside CHADTree's git root under `.vars/runtime`.

Running `rm -rf` on `chadtree/` will cleanly remove everything CHADTree installs to your local system.
