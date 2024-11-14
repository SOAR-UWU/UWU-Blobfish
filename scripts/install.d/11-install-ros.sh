#!/usr/bin/env bash
# Install ROS and stuff. Should be harmless if already installed.
# From now on, we do blanket installs, don't have to be too concerned about exact
# dependencies.

set -eo pipefail

# Jetson specific repository override.
if uname -a | grep -q "tegra"; then
  wget -qO - https://isaac.download.nvidia.com/isaac-ros/repos.key | sudo apt-key add -
  grep -qxF "deb https://isaac.download.nvidia.com/isaac-ros/release-3.0 $(lsb_release -cs) release-3.0" /etc/apt/sources.list || \
  echo "deb https://isaac.download.nvidia.com/isaac-ros/release-3.0 $(lsb_release -cs) release-3.0" | sudo tee -a /etc/apt/sources.list
fi

# Setup ROS2 Humble pkg repository.
# https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debs.html
sudo wget -qO /etc/apt/keyrings/ros-archive-keyring.gpg https://raw.githubusercontent.com/ros/rosdistro/master/ros.key
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(lsb_release -cs) main" \
  | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

# `ros-humble-desktop` and `ros-dev-tools` are blanket meta packages.
# `~nros-humble-rqt*` installs all rqt plugins.
sudo apt update
sudo apt install -y \
  python3-pip \
  ros-humble-desktop \
  ros-dev-tools \
  ~nros-humble-rqt*

if grep -q "#<<<$(basename $BASH_SOURCE)" ~/.bashrc; then
  echo 'ROS already sourced in "~/.bashrc".'
else
  echo "#<<<$(basename $BASH_SOURCE)" >> ~/.bashrc
  echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
fi

if [[ -f /etc/ros/rosdep/sources.list.d/20-default.list ]]; then
  echo "rosdep already initialized."
else
  source /opt/ros/humble/setup.bash
  sudo rosdep init
fi
