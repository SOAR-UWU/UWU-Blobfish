#!/usr/bin/env bash
# Install Gazebo. Should be harmless if already installed.

set -eo pipefail

# Setup OSRF Gazebo pkg repository.
# https://gazebosim.org/docs/harmonic/install_ubuntu
sudo wget -qO /etc/apt/keyrings/pkgs-osrf-archive-keyring.gpg https://packages.osrfoundation.org/gazebo.gpg
echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/pkgs-osrf-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable jammy main" \
  | sudo tee /etc/apt/sources.list.d/gazebo-stable.list > /dev/null

sudo apt update
sudo apt install -y ros-humble-ros-gzharmonic
