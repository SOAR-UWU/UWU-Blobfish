#!/usr/bin/env bash
# Don't put install steps in here, each distinct install process should be its own
# script in `install.d/`. This script is only for sourcing those scripts.

set -eu

# Directory this script is in.
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
# Directory of workspace root, assuming script is in `scripts/`.
WS_DIR=$(realpath "$SCRIPT_DIR"/..)

# Run all install scripts in order with the workspace root as the working directory.
for f in "$WS_DIR"/scripts/install.d/*; do
    if [[ $f == *.@(bash|sh) && -r $f ]]; then
        (cd "$WS_DIR" && source "$f")
    fi
done
