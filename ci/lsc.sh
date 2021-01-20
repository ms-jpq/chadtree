#!/usr/bin/env bash

set -eu
set -o pipefail


cd "$(dirname "$0")" || exit 1

FILE="$1"

eval "$(dircolors -b "$FILE")"
printf '%s' "$LS_COLORS"

exit 1