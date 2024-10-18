#!/usr/bin/env bash
# Insert commands to be run on host machine every time before container starts.
# I am not sure what happens for WSL though.

# Allow X11/XWayland forwarding.
if command -v xhost > /dev/null; then
  xhost +local:root
fi