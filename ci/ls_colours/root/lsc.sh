#!/usr/bin/env bash

set -eu
set -o pipefail

FILE="$1"
export TERM=xterm-256color
eval "$(dircolors -b "$FILE")"
printf '%s' "$LS_COLORS"
