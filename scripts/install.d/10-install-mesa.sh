#!/usr/bin/env bash
# Update mesa drivers for accelerated graphics for gazebo.

set -eo pipefail

sudo add-apt-repository ppa:oibaf/graphics-drivers -y

sudo apt update
sudo apt install -y \
  mesa-utils \
  vainfo \
  mesa-va-drivers
