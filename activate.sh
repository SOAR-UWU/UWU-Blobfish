#!/bin/env bash
dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)

# PUT .isaac_ros_common-config OPTIONS HERE
export CONFIG_IMAGE_KEY="ros2_humble.fixes.user.realsense.arduino.gazebo.udev.misc"
export CONFIG_DOCKER_SEARCH_DIRS=(../../../docker) # RELATIVE TO run_dev.sh

$dir/thirdparty/isaac_ros_common/scripts/run_dev.sh $dir
