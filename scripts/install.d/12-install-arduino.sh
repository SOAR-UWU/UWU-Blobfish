#!/usr/bin/env bash
# Install tools to flash the arduino bridge firmware. Should be harmless if already installed.

set -eo pipefail

# Install the arduino-cli command.
wget -qO- https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sudo BINDIR=/usr/local/bin sh

# Install tools.
arduino-cli core install arduino:avr
arduino-cli lib install SimpleSerialProtocol Servo
