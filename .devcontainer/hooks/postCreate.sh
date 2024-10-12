#!/usr/bin/env bash
# Insert commands to run when container is started for the first time.

# Allow apt index & package cache to persist.
sudo rm -f /etc/apt/apt.conf.d/docker-clean; \
  echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' | sudo tee /etc/apt/apt.conf.d/keep-cache

# The volume mount is created as root, so fix permissions here.
sudo chown -R vscode:vscode /home/vscode/.cache

# Run the native install script.
scripts/install.sh
