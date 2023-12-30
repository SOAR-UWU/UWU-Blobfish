"""Library with functions to interface with Arduino."""

import time
from typing import List
import os

import serial

# TODO read from config file instead of hardcode
NUM_MOTORS = 7

EOT_CHAR = b'\n'
MOTOR_VALUE_START = b'M'

ARDUINO_HEADERS = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', 'arduino')
)
BOARD_FQBN = "arduino:avr:mega"
ARDUINO_PORT = "/dev/ttyUSB0"
BAUD_RATE = 19200



class JetsonArduinoInterface:
    def __init__(self, ser: serial.Serial, endianness: str = 'l'):
        self.ser = ser
        self.endianness = endianness

    @property
    def endianness(self):
        return self._endianness

    @endianness.setter
    def endianness(self, endian: str):
        if endian != 'b' and endian != 'l':
            raise ValueError(
                f"Endianness should be represented as either 'b' or 'l', not {endian}"
            )
        self._endianness = endian

    def await_eot(self, timeout):
        """Wait for the EOT signal for timeout seconds.

        Args:
            timeout (int): seconds to wait for eot

        Returns:
            bool: True if EOT is read, False if not
        """
        start_time = time.time()
        while True:
            if self.ser.read() == EOT_CHAR:
                return True

            current = time.time()
            if current - start_time > timeout:
                return False

    def write_motor_values(self, vals: List[int]):
        """Write 7 motor values to the serial port (in the form of 7 uint16s
        in a row).

        Args:
            vals (List[int]): list of motor values
        """
        if len(vals) != NUM_MOTORS:
            raise ValueError(f"Length of motor values should be the same as \
the number of motors ({NUM_MOTORS})")

        # First write the init message
        self.ser.write(MOTOR_VALUE_START)

        # Then write motor values
        for val in vals:
            self.write_uint16(val)

        # Write EOT
        self.ser.write(EOT_CHAR)

    def write_uint16(self, n: int):
        """Write an integer to the serial port as an unsigned 16-bit integer.

        Args:
            n (int): Number to write
        """
        self._write_bytes(n, 2)

    def read_uint16(self):
        """Read an integer from the serial port as an unsigned integer.

        Returns:
            int: read integer value
        """
        return self._read_bytes(2)

    def read_uint64(self):
        return self._read_bytes(4)

    def _read_bytes(self, n_bytes: int):
        read_b = self.ser.read(n_bytes)
        if self.endianness == 'l':
            ret = int.from_bytes(read_b, 'little')
        else:
            ret = int.from_bytes(read_b, 'big')

        return ret

    def _write_bytes(self, n: int, n_bytes: int):
        if self.endianness == 'l':
            byte_n = n.to_bytes(n_bytes, 'little')
        else:
            byte_n = n.to_bytes(n_bytes, 'big')
        self.ser.write(byte_n)

    def wait_for_connection(self, startup_char: bytes, timeout: int):
        """Test for connection with Arduino.

        Blocks until either connection is established with the Arduino or the
        timeout is reached. Returns True when connected; False if timed out.

        Args:
            timeout (int): Time to wait in seconds. Set to 0 or less to never
            timeout.
        """
        start = time.time()
        while self.ser.read() != startup_char:
            time.sleep(1)
            current = time.time()
            if timeout > 0 and current - start > timeout:
                # timed out, stop attempting to connect
                return False

        self.ser.write(startup_char)
        # Signal received, connected. Return True.
        return True
