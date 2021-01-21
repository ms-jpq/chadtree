# Migration

Hello everybody, I am dropping support for `python_version < 3.8.2` for the main branch.

Please use the `legacy` branch if you cannot use newer versions of `python`.

I am very sorry about this, but I am doing this in order to support more awesome features.

## What you need to do:

**Windows Users, please use `legacy` branch for now, I [need help](https://github.com/ms-jpq/chadtree/issues/102) getting this to run under windows**

Change your extension manager to use the following:

```vim
Plug 'ms-jpq/chadtree', {'branch': 'chad', 'do': 'python3 -m chadtree deps'}

```

Run `:CHADdeps` the first time before you use `:CHADopen`

**Check out [`new configuration`](https://github.com/ms-jpq/chadtree/blob/future2/docs/CONFIGURATION.md)**. It is incompatible with the old one, BUT comes with a new parser and vaildator so the migration will be mostly just renaming one or two keys.

If you make a typo, CHADTree will tell you so!

## Why?

Several reasons:

Python `3.8.2` is the version of `python` on the latest Ubuntu LTS.

There are some features I wanted to add that strictly cannot be supported below `python 3.8`. For example, I wanted to include a spec validator, but `python 3.7` lacks support for `Literal` in the `typing` module, and therefore could introduce ambiguities in the parser.

The old CHADTree ran by `nvim`'s default extension implementation, which had major short comings:

1. Everything ran in the same process.

2. The user needs to call `:UpdateRemotePlugins` each time I add a new RPC end point, or else they will get a random confusing error.

3. [`pynvim`](https://github.com/neovim/pynvim) needed to be installed, For most users who aren't familiar with how `pip` and python modules work. This will either mess up their usage of `virtualenv`, or require a global or user level `pip` package just to use CHADTree.

In order to fix these issues, I will have to make breaking changes anyways, why not now?

## Solutions

At the cost of one time migration, which means users need to update their configs and perhaps python version. I will deilver enough features to warrant the upgrade.

## New Features

### Independent package management

CHADTree now will use all local dependencies. Which means `pynvim` can be installed under a subdirectory to `chadtree`. Doing a `rm -rf` on CHADTree will cleanly remove everything it brings in.

Nothing will pollute the global namespace for python.

### Isolated Process

CHADTree now runs inside an isolated process! Not only will it start faster, it will also be isolated from your other python plugins. Incase of errors or crashes, they will not affect each other nearly as much!

### New Vaildating Config Parser

CHADTree will now vaildate your typos and mis-understandings on how to configure it! No more silent failures. If you make a typo in the config, it will tell you loud and clear!

New `property.sub_property` syntax also supported on a recursive level.

### Faster startup

CHADTree started up kinda of slowly before. I have made it perceptibly faster through various marginal improvments.

### Bigly Improved Documentation

CHADTree now comes with it's own help command!

Use `:CHADhelp {topic}` to open up built-in help docs in a floating window.

Use `:CHADhelp {topic} --web` to open up the same help docs in a browser.

### Parallel File System Operations

Previously CHADTree was fast because it was async.

Now CHADTree can be even faster because it does things in parallel.

See [design document here](https://github.com/ms-jpq/chadtree/tree/future2/docs/ARCHITECTURE.md) for details.

### Vastly Improved Rendering Speed

You know how React is famous because it only renders what needs to be changed?

CHADTree now uses a React-like virtual rendering target. It only re-renders the minimal amount of lines. CHADTree can now handle thousands of visible files and still be reasonablly performant!

_This is only visible when you have 1000+ files visible. The old ways was fast enough for most tasks._

### Theming

Yub, this is yuge. The #1 request was for more themes. They have came!

Go see `:CHADhelp theme` for [details](https://github.com/ms-jpq/chadtree/tree/future2/docs/THEME.md).

### Even more Poilsh

- Maintain cursor position in many circumstances, ie. move root up / down, filtering for files, renaming, creating files, etc

- Selection of hidden / invisble files no longer possible.

- Retain selection when copying or moving files.

- Now shows `git submodules`

### Even Higher Quality Code

Yes the quailty of code is a feature. The better the code, the easier it is for me and other people to add in future improvements.
