#!/usr/bin/env bash

set -eo pipefail

# Directory this script is in.
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
# Directory of workspace root, assuming script is in `scripts/`.
WS_DIR=$(realpath "$SCRIPT_DIR"/..)

mode=irl
for arg in "$@"; do
  if [[ "$arg" == "-h" || "$arg" == "--help" ]]; then
    echo "Usage: $0 [irl|sim]"
    echo "Default mode is irl. Specify sim to run in simulation mode."
    echo "If tmux session already exists, ignore mode and attach to it."
    exit
  elif [[ "$arg" == "sim" ]]; then
    mode=sim
  fi
done

source install/setup.bash

if tmux ls | grep -q ros2; then
  tmux attach -t ros2
  exit
fi

launch_cmd="ros2 launch launch-all.py"
if [[ "$mode" == "sim" ]]; then
  launch_cmd="ros2 launch uwu_sim launch.py"
fi

# TODO: sim-irl hybrid mode.

# https://man7.org/linux/man-pages/man1/tmux.1.html
tmux new -ds ros2 -n launch "source install/setup.bash; ros2 launch launch-all.py" \; \
  neww -dn "monitor" "scripts/teleop.sh" \; \
  neww -dn "routine" "source install/setup.bash; ros2 launch blobfish_control routine.launch.py" \; \
  attach

# TODO: Other tmux scripts for sim and sim-irl hybrid testing.
