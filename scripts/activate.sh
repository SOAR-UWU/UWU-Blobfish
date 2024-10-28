#!/usr/bin/env bash
# Convenience script to source the project ROS overlay in a new subshell.

# Directory this script is in.
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
# Directory of workspace root, assuming script is in `scripts/`.
WS_DIR=$(realpath "$SCRIPT_DIR"/..)

# Don't let nesting occur.
if [[ -n "$__UWU_ENV" && "$1" != "--force" ]]; then
  echo "Already in UWU environment. Use 'reload' instead to refresh the environment."
  exit 1
fi

# Check if the workspace has been built.
if [[ ! -f "$WS_DIR"/install/setup.bash ]]; then
  echo "No install/setup.bash found. Did you run scripts/build.sh?"
  exit 1
fi

# Setup the overlay in a new subshell.
exec bash --init-file <(echo "\
  source ~/.bashrc;\
  cd \"$WS_DIR\";\
  alias deactivate='exit';\
  alias launch='ros2 launch';\
  reload() { echo Reloading UWU! && exec \"$WS_DIR\"/scripts/activate.sh --force; };\
  build() { \"$WS_DIR\"/scripts/build.sh \$@; reload; };\
  source install/local_setup.bash;\
  export PYTHONWARNINGS=ignore:::setuptools.command.install,ignore:::setuptools.command.easy_install,ignore:::pkg_resources;\
  export __UWU_ENV=1;\
  PS1=\"[UWU] \${PS1:-}\";\
")
