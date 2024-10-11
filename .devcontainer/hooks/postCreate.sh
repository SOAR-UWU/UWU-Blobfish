#!/bin/sh
# Insert commands to run when container is started for the first time.

sudo rm -f /etc/apt/apt.conf.d/docker-clean; \
  echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' | sudo tee /etc/apt/apt.conf.d/keep-cache

sudo chown -R vscode:vscode /home/vscode/.cache

scripts/install.sh
