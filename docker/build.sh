#!/usr/bin/env bash

set -eu
set -o pipefail


cd "$(dirname "$0")" || exit 1

IMAGE='chad'
docker build -f 'Dockerfile' -t "$IMAGE" .
