#!/usr/bin/env bash
# Misc stuff.

set -eo pipefail

# Enable openCL support (OpenCV uses it for hardware acceleration).
sudo mkdir -p /etc/OpenCL/vendors
echo "libnvidia-opencl.so.1" | sudo tee /etc/OpenCL/vendors/nvidia.icd > /dev/null
