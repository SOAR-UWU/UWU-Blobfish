#!/usr/bin/env bash

set -eo pipefail

# Directory this script is in.
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
# Directory of workspace root, assuming script is in `scripts/`.
WS_DIR=$(realpath "$SCRIPT_DIR"/..)

source install/setup.bash

if tmux ls | grep -q ros2; then
  tmux attach -t ros2
  exit
fi

# https://man7.org/linux/man-pages/man1/tmux.1.html
tmux new -ds ros2 -n launch "ros2 launch launch-all.py" \; \
  neww -dn "monitor" "scripts/teleop.sh" \; \
  neww -dn "routine" "ros2 launch blobfish_control routine.launch.py" \; \
  attach

# TODO: Other tmux scripts for sim and sim-irl hybrid testing.
