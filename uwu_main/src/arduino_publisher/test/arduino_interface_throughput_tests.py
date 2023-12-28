from import_context import arduino_interface as interface
from import_context import ARDUINO_HEADERS, BOARD_FQBN, ARDUINO_PORT, BAUD_RATE
import serial
import subprocess
import time
import os

ARDUINO_TEST_INO = os.path.abspath(os.path.join(os.path.abspath(__file__), "arduino_throughput", "arduino_throughput.ino"))

STARTUP_CHAR = b"S"
BENCHMARK_END_SIGNAL = b"E"

def startup():
    print("Compiling arduino code...")
    subprocess.run(["arduino-cli", "compile", "--fqbn", BOARD_FQBN, ARDUINO_TEST_INO, "--library", ARDUINO_HEADERS], check=True)
    print("Compiled")
    
def arduino_speed_benchmarks(wait_time: int = 30):
    subprocess.run(["arduino-cli", "upload", "-p", ARDUINO_PORT, "--fqbn", BOARD_FQBN, ARDUINO_TEST_INO], check=True)
    print("Uploaded to board.")


    ser = serial.Serial(ARDUINO_PORT, timeout = 5, baudrate=BAUD_RATE)
    jai = interface.JetsonArduinoInterface(ser)
    vals = [133, 434, 512, 123, 364, 125, 126]
    
    # Fail if connection is not established
    assert(jai.wait_for_connection(STARTUP_CHAR, 30))

    start_time = time.time()
    end_time = start_time

    
    while end_time - start_time < wait_time:
        jai.write_motor_values(vals)
        end_time = time.time()

    time.sleep(1)

    ser.write(BENCHMARK_END_SIGNAL)
    
    # Block until "M" is read
    while ser.read() != b'M': pass

    num_rec = jai.read_uint64()
    ser.close()
    return num_rec

if __name__ == "__main__":
    startup()
    insts = arduino_speed_benchmarks(10)
    insts_p_s = insts / 10
    print(f"Motor instructions per second: {insts_p_s}")
    