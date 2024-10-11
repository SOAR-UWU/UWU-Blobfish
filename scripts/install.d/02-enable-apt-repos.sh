#!/usr/bin/env bash
# Enable all apt repositories.

set -eo pipefail

# Superfluous, but just to be sure.
add-apt-repository -y main
add-apt-repository -y restricted
add-apt-repository -y universe
add-apt-repository -y multiverse
