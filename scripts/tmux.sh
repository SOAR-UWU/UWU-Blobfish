#!/usr/bin/env bash

set -eo pipefail

# Directory this script is in.
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
# Directory of workspace root, assuming script is in `scripts/`.
WS_DIR=$(realpath "$SCRIPT_DIR"/..)

source install/setup.bash

tmux new-session -s ros2 "ros2 launch launch-all.py" \; \
  new-window -n "monitor" "scripts/teleop.sh" \; \
  new-window -n "routine" "ros2 run blobfish_control rocket" \;
