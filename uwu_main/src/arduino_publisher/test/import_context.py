import os
import sys

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), ".."))
)

import arduino_publisher.arduino_interface as arduino_interface

ARDUINO_HEADERS = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', 'include', 'arduino')
)
BOARD_FQBN = "arduino:avr:nano:cpu=atmega328old"
ARDUINO_PORT = "/dev/ttyUSB0"
BAUD_RATE = 19200
