#!/usr/bin/env bash
# Enable all apt repositories. Should run first.

set -eo pipefail

sudo apt update
sudo apt install -y software-properties-common

# Some are superfluous, but just to be sure.
sudo add-apt-repository -y main
sudo add-apt-repository -y restricted
sudo add-apt-repository -y universe
sudo add-apt-repository -y multiverse

# Ensure keyrings directory exists later.
sudo mkdir -p /etc/apt/keyrings
