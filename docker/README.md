# Docker quickstart
[Read the official NVIDIA documentation on this!](https://nvidia-isaac-ros.github.io/repositories_and_packages/isaac_ros_common/index.html#isaac-ros-docker-development-environment)

This folder contains the Dockerfile to configure the Jetson environment. To start the Docker container:

1. Check that `isaac_ros_common` has been downloaded in the `home` (`~`) directory. If not, follow the instructions in [this document](https://docs.google.com/document/d/1cREZMxORv1iL8ImSttAo6MXFEE-e809aip0bS_fPoG4/edit?usp=sharing) to downlaod and install the Isaac ROS Docker system.
2. In the `home` (`~`) directory, create a folder `workspaces/isaac_ros-dev`, and **clone this repo inside that directory**.
3. In the `isaac_ros_common/scripts` folder, check that the script `run_dev.sh` exists.
4. In the **same folder as `run_dev.sh`** (`isaac_ros_common/scripts` by default), create a file called `.isaac_ros_common-config` with the following content:
```bash
CONFIG_IMAGE_CONFIG_IMAGE_KEY="ros2_humble.user.uwu"
CONFIG_DOCKER_SEARCH_DIRS=(~/workspaces/isaac_ros-dev/UWU-Blobfish/docker)   # this is a path to **this folder** on your system.
```
5. Run the script `run_dev.sh` to start the Docker container.
