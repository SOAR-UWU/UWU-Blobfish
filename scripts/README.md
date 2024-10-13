# UWU Blobfish Scripts

## Key Scripts

- `install.sh`: Prepares ROS2 environment and necessary tools that are beyond the scope of the project dependencies or `rosdep`.

## Convenience Scripts

- `build.sh`: Installs project dependencies, the `requirements.txt` hack, and builds all packages.
  - Specify package names to build only those packages.
- `activate.sh`: Sources the project ROS overlay in a new subshell.
  - `deactivate`/`exit` to exit the subshell.
  - `reload` to reload the overlay after changes.
  - `build` to run `build.sh` and `reload` in one command. Package names can be specified.
