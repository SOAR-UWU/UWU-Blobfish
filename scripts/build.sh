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
  env -iC "$WS_DIR" bash \
    -c "$(echo " \
      . /opt/ros/humble/setup.bash; \
      (cd install/ && rm -rf $@); \
      PYTHONWARNINGS=ignore:::setuptools.command.install,ignore:::setuptools.command.easy_install,ignore:::pkg_resources \
      colcon build --symlink-install --packages-up-to $@ \
    ")"
  exit 0
fi

# Full build.
source /opt/ros/humble/setup.bash
rosdep update
(cd "$WS_DIR" && rosdep install --from-paths . --ignore-src -y)
# Build in login shell to avoid underlay override warning.
env -iC "$WS_DIR" bash \
  -c "$(echo " \
    . /opt/ros/humble/setup.bash; \
    rm -rf install/ build/; \
    PYTHONWARNINGS=ignore:::setuptools.command.install,ignore:::setuptools.command.easy_install,ignore:::pkg_resources \
    colcon build --symlink-install \
  ")"
