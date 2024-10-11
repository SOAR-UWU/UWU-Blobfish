#!/usr/bin/env bash
# Don't put install steps in here, each distinct install process should be its own
# script in `install.d/`. This script is only for sourcing those scripts.

set -eu

# Make sure we are on Ubuntu/Ubuntu WSL, not git bash or other distros.
if [[ $(source /etc/os-release && echo $ID) != "ubuntu" ]]; then
  echo "This script is only supported on Ubuntu/Ubuntu WSL."
  echo "You are on: $(source /etc/os-release && echo $ID)"
  exit 1
fi

# Force script to run as root.
# NOTE: What if some scripts need the current user? Better to use `sudo` when needed.
# This has the downside that if the script runs for a long time, the password might
# have to be entered again.
# if [[ $(id -u) -ne 0 ]]; then
#   echo Please run this script as root or using sudo!
#   exit 1
# fi

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
