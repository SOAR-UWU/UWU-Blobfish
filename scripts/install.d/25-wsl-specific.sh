#!/usr/bin/env bash
# Windows Subsystem for Linux (WSL) specific setup steps.

set -eo pipefail

# Check for presence of /usr/lib/wsl.
if [[ ! -d /usr/lib/wsl ]]; then
  echo "WSL not detected. Skipping WSL-specific setup."
  exit 0
fi

# Add a marker so we know this script has been run before.
if grep -q "#<<<25-wsl-specific.sh" /etc/bash.bashrc; then
  echo "25-wsl-specific.sh already ran once."
  exit 0
fi
echo "#<<<25-wsl-specific.sh" | sudo tee -a /etc/bash.bashrc > /dev/null

# Harmless on Linux, necessary on WSL for gui accel (compute accel still works without).
echo "export LD_LIBRARY_PATH=/usr/lib/wsl/lib:\${LD_LIBRARY_PATH}" | sudo tee -a /etc/bash.bashrc > /dev/null
echo "export LIBVA_DRIVER_NAME=d3d12" | sudo tee -a /etc/bash.bashrc > /dev/null
# I think it falls back if a Nvidia GPU isn't found, but not sure.
echo "export MESA_D3D12_DEFAULT_ADAPTER_NAME=NVIDIA" | sudo tee -a /etc/bash.bashrc > /dev/null
