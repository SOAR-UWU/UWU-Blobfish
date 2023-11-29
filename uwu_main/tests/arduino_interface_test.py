import pytest
from import_context import arduino_interface as interface
import serial
import subprocess

BOARD_FQBN = "arduino:avr:mega"
ARDUINO_PORT = "/dev/ttyUSB0"
ARDUINO_TEST_INO = "arduino_test/arduino_test.ino"
ARDUINO_SOURCE_FILES = "../../arduino"

STARTUP_CHAR = b"S"

@pytest.fixture(scope="module")
def startup():
    print("Compiling arduino code...")
    subprocess.run(["arduino-cli", "compile", "--fqbn", BOARD_FQBN, ARDUINO_TEST_INO, "--library", ARDUINO_SOURCE_FILES])
    print("Compiled")

def test_connection_init():
    subprocess.run(["arduino-cli", "upload", "-p", ARDUINO_PORT, "--fqbn", BOARD_FQBN, ARDUINO_TEST_INO])
    print("Uploaded to board.")
    ser = serial.Serial(ARDUINO_PORT, timeout=30)
    assert(interface.wait_for_connection(ser, STARTUP_CHAR, 30))
    ser.close()

def test_send_motor_values():
    subprocess.run(["arduino-cli", "upload", "-p", ARDUINO_PORT, "--fqbn", BOARD_FQBN, ARDUINO_TEST_INO])
    print("Uploaded to board.")
    ser = serial.Serial(ARDUINO_PORT, timeout = 5)
    vals = [133, 434, 512, 123, 364, 125, 126]
    interface.wait_for_connection(ser, STARTUP_CHAR, 30)
    interface.write_motor_values(ser, vals)
    recv = []

    # Block until "M" is read
    while ser.read() != b'M': pass

    for _ in vals:
        recv.append(interface.read_uint16(ser))
    assert(recv == vals)
    ser.close()

if __name__ == "__main__":
    test_send_motor_values()
