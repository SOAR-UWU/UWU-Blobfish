#!/usr/bin/env bash
# Install ROS and stuff. Should be harmless if already installed.
# From now on, we do blanket installs, don't have to be too concerned about exact
# dependencies.

set -eo pipefail

# Setup ROS2 Humble pkg repository.
# https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debs.html
sudo wget -qO /etc/apt/keyrings/ros-archive-keyring.gpg https://raw.githubusercontent.com/ros/rosdistro/master/ros.key
echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu jammy main" \
  | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

# `ros-humble-desktop` and `ros-dev-tools` are blanket meta packages.
# `~nros-humble-rqt*` installs all rqt plugins.
sudo apt update && sudo apt install -y \
  ros-humble-desktop \
  ros-dev-tools \
  ~nros-humble-rqt*

echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
source /opt/ros/humble/setup.bash
sudo rosdep init
