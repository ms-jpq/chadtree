# Migration

Hello everybody, I am dropping support for `python_version < 3.8.2` for the main branch.

Please use the `legacy` branch if you cannot use newer versions of `python`.

I am very sorry about this, but I am doing this in order to support more awesome features.

## Why?

Several reasons:

Python 3.8 is the version of `python` on the latest Ubuntu LTS.

There are some features I wanted to add that strictly cannot be supported below `python 3.8`. For example, I wanted to include a spec validator, but `python 3.7` lacks support for `Literal` in the `typing` module, and therefore could introduce ambiguities in the parser.

The old CHADTree ran by `nvim`'s default extension implementation, which had major short comings:

1) Everything ran in the same process.

2) The user needs to call `:UpdateRemotePlugins` each time I add a new RPC end point, or else they will get a random confusing error.

3) [`pynvim`](https://github.com/neovim/pynvim) needed to be installed, For most users who aren't familiar with how `pip` and python modules work. This will either mess up their usage of `virtualenv`, or require a global or user level `pip` package just to use CHADTree.

## Solutions

At the cost of one time migration, which means users need to update their configs and perhaps python version. I will deilver enough features to warrant the upgrade.

## New Features

### Independent package management

CHADTree now will use all local dependencies. Which means `pynvim` can be installed under a subdirectory to `CHADTree`. Doing a `rm -rf` on `CHADTree` will cleanly remove everything it brings in.

### Isolated Process

CHADTree now runs inside an isolated process! Not only will it start faster, it will also be isolated from your other python plugins. Incase of errors or crashes, they will not affect each other nearly as much!

### New Config Parser

CHADTree will now vaildate your typos and mis-understandings on how to configure it! No more silent failures. If you make a typo in the config, it will tell you loud and clear!

### Faster startup

CHADTree started up kinda of slowly before. I have made it perceptibly faster through various marginal improvments.

### Bigly Improved Documentation

CHADTree now comes with it's own help command!

Use `:CHADhelp {topic}` to