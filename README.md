# UWU-Blobfish

Code for a submersible.

## Installation

### UWU Thumbdrive

TODO.

### Native Ubuntu 22.04

TODO.

### Devcontainers (WSL/Linux)

TODO.

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
