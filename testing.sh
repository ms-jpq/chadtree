#!/usr/bin/env bash

set -eu
set -o pipefail


cd "$(dirname "$0")" || exit 1

export NVIM_LISTEN_ADDRESS=/tmp/nvim
exec nvim
