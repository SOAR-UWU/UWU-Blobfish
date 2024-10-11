#!/usr/bin/env bash
# Use udev to assign fixed device nodes to our sensors.

set -eo pipefail

sudo mkdir -p /etc/udev/rules.d
sudo cp scripts/install.d/files/99-uwu-blobfish-dev-detect.rules /etc/udev/rules.d/99-uwu-blobfish-dev-detect.rules
