#!/usr/bin/env bash
# Install Gazebo. Should be harmless if already installed.

set -eo pipefail

# TODO: Build from source? Look harder? Maybe the stable pair is built for arm64 focal?
if uname -a | grep -q "tegra"; then
  echo "Skipping $(basename $BASH_SOURCE) on Jetson."
  exit 0
fi

# Setup OSRF Gazebo pkg repository.
# https://gazebosim.org/docs/harmonic/install_ubuntu
sudo wget -qO /etc/apt/keyrings/pkgs-osrf-archive-keyring.gpg https://packages.osrfoundation.org/gazebo.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/pkgs-osrf-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" \
  | sudo tee /etc/apt/sources.list.d/gazebo-stable.list > /dev/null

sudo apt update
sudo apt install -y ros-humble-ros-gzharmonic
