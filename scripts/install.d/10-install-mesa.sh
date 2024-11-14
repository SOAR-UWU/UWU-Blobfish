#!/usr/bin/env bash
# Update mesa drivers for accelerated graphics for gazebo.

set -eo pipefail

if uname -a | grep -q "tegra"; then
  echo "Skipping $(basename $BASH_SOURCE) on Jetson."
  exit 0
fi

sudo add-apt-repository ppa:oibaf/graphics-drivers -y

sudo apt update
sudo apt install -y \
  mesa-utils \
  vainfo \
  mesa-va-drivers
