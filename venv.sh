#!/usr/bin/env bash

set -eu
set -o pipefail

cd "$(dirname "$0")" || exit 1

# if [[ 1 ]]
# then
#   PREPEND = ""
# else
#   PREPEND = "$PWD"
# fi

export PATH="$PWD/.vars/runtime/bin:$PATH"
exec "$@"