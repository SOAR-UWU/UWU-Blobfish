#!/usr/bin/env bash
# Insert commands to be run on host machine every time before container starts.
# Will run correctly if repository is located in WSL filesystem. However, will fail
# if located on Windows filesystem (it will try and use CMD to run it).

# Allow X11/XWayland forwarding.
if command -v xhost > /dev/null; then
  xhost +local:
fi
