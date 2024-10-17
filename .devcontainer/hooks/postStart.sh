#!/usr/bin/env bash
# Insert commands to run every time the container is started.
# Unfortunately, WSL's GID for render is inconsistent so I can't "group_add" the user.
sudo chmod 777 /dev/dri/renderD128
