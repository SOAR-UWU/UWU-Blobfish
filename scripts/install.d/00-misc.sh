#!/usr/bin/env bash
# Misc stuff. Should run instantly and be order-independent given 00 prefix.

set -eo pipefail

if uname -a | grep -q "tegra"; then
  echo "Skipping $(basename "$0") on Jetson."
  exit 0
fi

# Enable openCL support for Nvidia (OpenCV uses it for hardware acceleration).
sudo mkdir -p /etc/OpenCL/vendors
echo "libnvidia-opencl.so.1" | sudo tee /etc/OpenCL/vendors/nvidia.icd > /dev/null
