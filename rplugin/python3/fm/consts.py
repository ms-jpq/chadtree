from os.path import dirname, join


__base__ = dirname(dirname(dirname(dirname(__file__))))
__config__ = join(__base__, "config")

fm_filetype = "neovimasyncfm"

keymap_json = join(__config__, "keymap.json")
icons_json = join(__config__, "icons.json")
ignore_json = join(__config__, "ignore.json")
