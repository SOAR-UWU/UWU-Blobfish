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

**Note**: Resetting the environment is necessary if any `Dockerfile` is modified, or if `CONFIG_IMAGE_KEY` inside `.isaac_ros_common-config` is changed, to rebuild the container so that changes take effect.

**Note**: For an alternative workflow using VSCode Dev Containers (which support Python Intellisense), you can use "> Dev Containers: Attach to Running Container...", see: <https://code.visualstudio.com/docs/devcontainers/attach-container>.

### Native ROS2

Refer to the documentation on Google Drive.

## Developer Guide

- New ROS2 packages should be added to `src/`.
- Third-party packages should be added via `git submodule` to `thirdparty/`.
  - Fork third-party packages to our org if you need to make modifications.
- Arduino code should be added to `arduino/`.
- Create a file named `COLCON_IGNORE` (i.e., `touch COLCON_IGNORE`) in folders containing ROS2 packages you don't want colcon to build.

### Folder Structure

See respective `README.md` files in each folder for more information.

- `arduino/`: Arduino code.
- `docker/`: Additional image layers for the ISAAC ROS Docker Environment.
- `src/`: First-party ROS2 packages.
- `thirdparty/`: Third-party ROS2 packages added as git submodules.

### Camera Stuff

Cause the realsense viewer doesn't work on my (J-H) container for some reason, plus we now have that totally crap oversaturation issue with the D455 (see last page of <https://www.intelrealsense.com/download/13629/>), we are using a regular usb cam. So here's the ros2 usb cam node:

```sh
sudo apt install ros-humble-usb-cam
ros2 run usb_cam usb_cam_node_exe --ros-args -p video_device:=/dev/video4
```

See literally the source code for the parameters: <https://github.com/ros-drivers/usb_cam/blob/70ed391a979287bad056c9e75bad8c2001a98f2b/src/ros2/usb_cam_node.cpp#L65-L85>

Surprisingly, most of the node's parameters can be changed live via `rqt`, so that's a good way to figure out what does what and calibrate.
