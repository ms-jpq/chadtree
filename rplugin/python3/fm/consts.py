from os.path import dirname, join

__base__ = dirname(dirname(dirname(dirname(__file__))))
__config__ = join(__base__, "config")

config_json = join(__config__, "config.json")
icons_json = join(__config__, "icons.json")
ignore_json = join(__config__, "ignore.json")

fm_filetype = "fast_fm"
