# UWU-Blobfish

Code for a submersible.

## Installation

If using the Nvidia Jetson or a Nvidia GPU, using the [ISAAC ROS Docker Environment](#isaac-ros-docker-environment) method is recommended. Otherwise, refer to the documentation on Google Drive.

### ISAAC ROS Docker Environment

Ensure [Docker](https://www.docker.com/get-started/) for your OS is installed. For recent versions of Windows and Docker, Nvidia GPU support should be built-in. For Linux, follow the [Nvidia Docker installation instructions](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html).

In a terminal (current directory doesn't matter), run:

```sh
./activate.sh
```

This will open a shell inside the Docker container with a pre-defined environment, **and the entire repository mounted as `/workspaces/isaac_ros-dev`**. Subsequent runs of `activate.sh` re-use the same container instead of creating a new one. To reset the environment, remove the container by running the following command on the host machine:

```sh
docker rm -f isaac_ros_dev-container
```

**Note**: Resetting the environment is necessary if any `Dockerfile` is modified, or if `CONFIG_IMAGE_KEY` inside `.isaac_ros_common-config` is changed, in order for the changes to take effect.

**Note**: For an alternative workflow using VSCode Dev Containers (which support Python Intellisense), you can use "> Dev Containers: Attach to Running Container...", see: <https://code.visualstudio.com/docs/devcontainers/attach-container>.

### Native ROS2

Refer to the documentation on Google Drive.

## Developer Guide

New ROS2 packages should be added to `uwu_main/src/`. Third-party packages should be added via `git subtree` to `uwu_main/`. Arduino code should be added to `arduino/`.

### Folder Structure

See respective `README.md` files in each folder for more information.

- `arduino/`: Arduino code.
- `data/`: Arbitrary data files for the sub like config files, model weights, etc.
- `docker/`: Additional image layers for the ISAAC ROS Docker Environment.
- `uwu_main/`: ROS2 code, including first-party and third-party packages.
  - `src/`: First-party ROS2 packages.
  - Other folders are third-party packages added via `git subtree`.

### Git Subtrees Used

Below commands are for updating subtrees. Note for subtrees to remain updatable, **commits must not modify both the subtree and the parent repo simultaneously**! Use two separate commits instead.

```sh
# NVIDIA-ISAAC-ROS/isaac_ros_common
git subtree pull --prefix uwu_main/isaac_ros_common https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_common.git main --squash

# ???/vectornav
# TODO: @javin where did you get it from?
```

See <https://craftquest.io/guides/git/git-workflow-tools/git-subtrees> for how to use subtrees. See <https://stackoverflow.com/questions/32407634/when-to-use-git-subtree> for when to use subtrees.

### Pre-commit Installation

Pre-commit automatically runs Git hooks to check your code when you commit to this repo.

First, install the pre-commit tool:

```sh
pip install pre-commit
```

Next, install the pre-commit hooks on your system:

```sh
pre-commit install
```

Pre-commit should run automatically when attempting to commit. If it doesn't, run the following after staging your changes:

```sh
pre-commit run
```

I haven't tested these hooks, so let me know if there's any problems. -Javin
