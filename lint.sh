#!/usr/bin/env bash

set -eu
set -o pipefail


cd "$(dirname "$0")" || exit 1

FILES=(
  *.py
  rplugin/python3/fancy_fm/*.py
  )

mypy --ignore-missing-imports -- "${FILES[@]}"
