import time
import pytest
from import_context import arduino_interface as interface
import serial
import subprocess

BOARD_FQBN = "arduino:avr:nano"
ARDUINO_PORT = "/dev/ttyUSB0"
ARDUINO_TEST_INO = "arduino_test/arduino_test.ino"
ARDUINO_SOURCE_FILES = "../../arduino"

STARTUP_CHAR = b"S"


"""Startup function for tests. Compiles Arduino code before upload.
"""
@pytest.fixture(scope="module")
def startup():
    print("Compiling arduino code...")
    subprocess.run(["arduino-cli", "compile", "--fqbn", BOARD_FQBN, ARDUINO_TEST_INO, "--library", ARDUINO_SOURCE_FILES], check=True)
    print("Compiled")

"""Test the connection handshake with Arduino. Fails if connection is not established after 30 seconds.
"""
def test_connection_init(startup):
    timeout = 30

    subprocess.run(["arduino-cli", "upload", "-p", ARDUINO_PORT, "--fqbn", BOARD_FQBN, ARDUINO_TEST_INO], check=True)
    print("Uploaded to board.")
    ser = serial.Serial(ARDUINO_PORT, timeout)
    assert(interface.wait_for_connection(ser, STARTUP_CHAR, 30))
    ser.close()

"""Test the sending of 1 set of motor values to Arduino.
"""
def test_send_motor_values(startup):
    serial_timeout = 5
    timeout = 30
    
    subprocess.run(["arduino-cli", "upload", "-p", ARDUINO_PORT, "--fqbn", BOARD_FQBN, ARDUINO_TEST_INO], check=True)
    print("Uploaded to board.")
    ser = serial.Serial(ARDUINO_PORT, serial_timeout)
    vals = [133, 434, 512, 123, 364, 125, 126]
    assert(interface.wait_for_connection(ser, STARTUP_CHAR, 30))
    interface.write_motor_values(ser, vals)
    recv = []

    start_time = time.time()
    # Block until "M" is read, or timeout
    while ser.read() != b'M':
        if time.time() - start_time > timeout:
            pytest.fail("Timed out while awaiting response from Arduino")

    for _ in vals:
        recv.append(interface.read_uint16(ser))
    assert(recv == vals)
    ser.close()

if __name__ == "__main__":
    startup()
