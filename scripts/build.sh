#!/usr/bin/env bash
# Convenience script to rosdep install everything and colcon build everything.

set -eo pipefail

# Directory this script is in.
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
# Directory of workspace root, assuming script is in `scripts/`.
WS_DIR=$(realpath "$SCRIPT_DIR"/..)

# Suppress warnings due to https://github.com/colcon/colcon-core/issues/454.
export PYTHONWARNINGS=ignore:::setuptools.command.install,ignore:::setuptools.command.easy_install,ignore:::pkg_resources

# Quick version that only builds specific packages and their dependencies.
if [[ "$#" -ge 1 ]]; then
  (cd "$WS_DIR" && colcon build --symlink-install --packages-up-to "$@")
  exit 0
fi

# Full build.
rosdep update
(cd "$WS_DIR" && rosdep install --from-paths . --ignore-src -y)
(cd "$WS_DIR" && colcon build --symlink-install)
