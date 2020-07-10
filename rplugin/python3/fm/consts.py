from os.path import dirname, join

__base__ = dirname(dirname(dirname(dirname(__file__))))
config_json = join(__base__, "config.json")
icons_json = join(__base__, "icons.json")

fm_filetype = "neovimasyncfm"
