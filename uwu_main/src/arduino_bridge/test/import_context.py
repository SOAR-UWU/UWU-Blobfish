import os
import sys

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), ".."))
)

import arduino_publisher.arduino_interface as arduino_interface
from arduino_publisher.arduino_interface import ARDUINO_HEADERS, BOARD_FQBN, ARDUINO_PORT, BAUD_RATE
