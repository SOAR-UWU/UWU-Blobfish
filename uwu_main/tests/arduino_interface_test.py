from import_context import arduino_interface as interface
import serial
import subprocess

BOARD_FQBN = "arduino:avr:mega"
ARDUINO_PORT = "/dev/ttyUSB0"
ARDUINO_TEST_INO = "arduino_test/arduino_test.ino"

STARTUP_CHAR = b"S"


def test_connection_init():
    ser = serial.Serial(ARDUINO_PORT)
    print("Compiling arduino code...")
    subprocess.run(["arduino-cli", "compile", "--fqbn", BOARD_FQBN, ARDUINO_TEST_INO])
    print("Compiled, uploading...")
    subprocess.run(["arduino-cli", "upload", "-p", ARDUINO_PORT, "--fqbn", BOARD_FQBN, ARDUINO_TEST_INO])
    print("Uploaded to board.")
    assert(interface.wait_for_connection(ser, STARTUP_CHAR, 30))

if __name__ == "__main__":
    test_connection_init()
