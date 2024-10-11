#!/usr/bin/env bash
# Use udev to assign fixed device nodes to our sensors.

set -eo pipefail

sudo cp scripts/install.d/files/99-uwu-blobfish-dev-detect.rules /etc/udev/rules.d/99-uwu-blobfish-dev-detect.rules
