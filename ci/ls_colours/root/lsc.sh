#!/usr/bin/env bash

set -eu
set -o pipefail


FILE="$1"
printf '%s' "$(dircolors -b "$PWD/$FILE")"
# printf '%s' "$LS_COLORS"
