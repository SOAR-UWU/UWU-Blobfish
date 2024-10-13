# UWU-Blobfish

Code for a submersible.

## Installation

### UWU Thumbdrive

While the UWU thumbdrive is setup with many useful things, there are some additional project-specific things in the project install script. See [Native Install](#native-install) below for the steps.

### Native Install

You must be using Ubuntu 22.04 as our project is based on ROS2 Humble. After cloning this repository to your preferred coding folder, run the following command inside the repository:

```sh
scripts/install.sh
```

That's it! The script will ensure all dependencies, even ROS2, are installed if they aren't already. Afterwards, run whatever you need to run. See [Common Commands](#common-commands) for some common commands.

### Devcontainers (Windows/Linux)

The official tutorial for installing Devcontainers on Windows or Linux: <https://code.visualstudio.com/docs/devcontainers/tutorial>

As per the tutorial, run "Dev Containers: Reopen in Container" from the command palette. `scripts/install.sh` will be run automatically. Afterwards, see [Common Commands](#common-commands) for some common commands.

I've done a lot of black magic behind the scenes to ensure GUI apps are forwarded out of the container, regardless of whether you're on Windows or Linux. Also regardless of if you use WSLg, Wayland or X11. It will also prefer the discrete GPU, falling back to the integrated GPU if necessary. For Linux (X11/XWayland), remember to `xhost +local:root` before running any GUI apps.

If you do not have a Nvidia GPU, comment out the below line in [`.devcontainer/compose.yaml`](.devcontainer/compose.yaml):

```yaml
services:
  devcontainer:
    # Comment out if you don't have a Nvidia GPU.
    # <<: *nvidia-opts
```

### Known Issues

#### Devcontainers (Windows)

- If Gazebo fails to load worlds complaining about "OGRE" and "allocation", completely stop the container and restart it. There is a memory leak when using the iGPU.
- Loading complex Gazebo worlds, especially for the first time, will take a long time. The window will be black and appear frozen. This is normal so just wait. Loading an empty world is a faster way to test if Gazebo is working.

### Common Commands

```sh
rosdep install -i --from-paths . -y
colcon build --symlink-install
colcon build --symlink-install --packages-up-to <package_names...>
source install/setup.bash
ros2 launch launch-all.py
```

## Developer Guide

- New ROS2 packages should be added to `src/`.
- Third-party packages should be added via `git submodule` to `thirdparty/`.
  - Fork third-party packages to our org if you need to make modifications.
- Arduino code should be added to `arduino/`.
- Create a file named `COLCON_IGNORE` (i.e., `touch COLCON_IGNORE`) in folders containing ROS2 packages you don't want colcon to build.

### Folder Structure

See respective `README.md` files in each folder for more information.

- `arduino/`: Arduino code.
- `scripts/`: Both convenience and important key scripts. See [`scripts/README.md`](scripts/README.md).
- `src/`: First-party ROS2 packages.
- `thirdparty/`: Third-party ROS2 packages added as git submodules.

### Camera Stuff

Cause the realsense viewer doesn't work on my (J-H) container for some reason, plus we now have that totally crap oversaturation issue with the D455 (see last page of <https://www.intelrealsense.com/download/13629/>), we are using a regular usb cam. So here's the ros2 usb cam node:

```sh
sudo apt install ros-humble-usb-cam
ros2 run usb_cam usb_cam_node_exe --ros-args -p video_device:=/dev/video4

# Video recording node
ros2 run debug_cv record_vid --ros-args -p img_topic:=/image_raw

# CV testing mode (using your webcam)
ros2 launch debug_cv test.launch.py
```

See literally the source code for the parameters: <https://github.com/ros-drivers/usb_cam/blob/70ed391a979287bad056c9e75bad8c2001a98f2b/src/ros2/usb_cam_node.cpp#L65-L85>

Surprisingly, most of the node's parameters can be changed live via `rqt`, so that's a good way to figure out what does what and calibrate.
