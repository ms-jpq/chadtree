#!/usr/bin/env bash

set -eu
set -o pipefail


cd "$(dirname "$0")" || exit 1

FILES=(
  ci/*.py
  rplugin/python3/chadtree/*.py
  )

mypy -- "${FILES[@]}"
