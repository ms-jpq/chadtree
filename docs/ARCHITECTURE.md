# Architecture

## Asynchronous Event Loop

CHADTree uses it's own event loop aside from the `asyncio` one defined by the [`pynvim` client](https://github.com/neovim/pynvim).

In fact, `pynvim` doesn't even run in the main thread.

All RPC notifications from the `nvim` server are sent to a global message queue, which is then processed in order of arrival after initialization code.

No further messages can be processed until the previous ones have.

`nvim` never blocks on the notifications. The CHADTree client has no blocking API.

## Parallelism

CHADTree uses a traditional threadpool for parallelizable operations, this includes querying for `git` status and file system walking, as well as other minor ones such as `mv` or `cp`.

The fs walk is done using a native parallel BFS strategy with a chunking step to avoid flooding the thread pool. This is not optimal since a [Fork Join](https://en.wikipedia.org/wiki/Fork%E2%80%93join_model) model should be more efficient.

However, as benchmarked, the performance bottleneck is in fact not the filesystem, but text & decorations rendering.

## Virtual Rendering

It turns out, if you have thousands lines of text with decorations such as colour or virtual text, `nvim` struggles to update buffers, even if you batch the render in a single call.

The answer is to have a virtual render target, and to compute the minimal necessary render instructions.

Previously I had written [Noact](https://github.com/ms-jpq/noact), a 70 line React like virtual dom engine. CHADTree works similarly, except with a more sophisticated diff algorithm, since the native approach does not cope with flat lists. (A flat list is a degenerate tree)

Instead of Virtual DOM nodes, a hash is used for each desired line of the render target.

## Memorylessness

CHADTree is designed with [Memorylessness](https://en.wikipedia.org/wiki/Memorylessness) in mind. For the most part the state transitions in CHADTree follow the Markov Property in that each successive state is independent from history.

## Pipelining

Broadly speaking, CHADTree has a two stage pipeline. The first stage processes messages, and generates render and cursor placement instructions for the second stage.

Ideally the first stage should be referentially transparent, with zero side effects, while the second stage executes all of the side effects. However, this is too tedious, a memoryless approach is taken for the two stages instead.