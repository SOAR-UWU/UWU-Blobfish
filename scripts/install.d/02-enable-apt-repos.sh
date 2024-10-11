#!/usr/bin/env bash
# Enable all apt repositories.

set -eo pipefail

sudo apt update && sudo apt install -y software-properties-common

# Some are superfluous, but just to be sure.
sudo add-apt-repository -y main restricted universe multiverse
