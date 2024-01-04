# Additional ISAAC ROS Docker Image Layers

[Read the official ISAAC ROS documentation on this!](https://nvidia-isaac-ros.github.io/repositories_and_packages/isaac_ros_common/index.html#isaac-ros-docker-development-environment)

This folder contains additional Dockerfiles to further customize the Isaac ROS Docker environment which will be used on the Jetson. To start the Docker container:

```sh
# Runs `run_dev.sh` with the root of this repository mounted as `/workspaces/isaac_ros-dev`.
./activate.sh
```

Additional Dockerfiles can be added by modifying `.isaac_ros_common-config` in the root of this repository. See [here for more configuration options](https://nvidia-isaac-ros.github.io/repositories_and_packages/isaac_ros_common/index.html#configuring-run-dev-sh).

```sh
CONFIG_IMAGE_KEY="ros2_humble.user.realsense.arduino"
CONFIG_DOCKER_SEARCH_DIRS=(../../../docker) # Relative to `uwu_main/isaac_ros_common/scripts/`.
```
