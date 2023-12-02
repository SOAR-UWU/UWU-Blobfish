"""Library with functions to interface with Arduino."""

import time
from typing import List

import serial

# TODO read from config file instead of hardcode
NUM_MOTORS = 7

EOT_CHAR = b'\n'

def write_motor_values(ser: serial.Serial, vals: List[int], endianness: str = 'l'):
    """Write 7 motor values to the serial port (in the form of 7 uint16s in a row).

    Args:
        ser (serial.Serial): Serial object to write to
        vals (List[int]): list of motor values
        endianness (str, optional): Endian-ness setting, 'b' for big and 'l' for little. 
            Defaults to 'l'.
    """
    if len(vals) != NUM_MOTORS:
        raise ValueError(f"Length of motor values should be the same as the number of motors ({NUM_MOTORS})")
    
    # First write the init message
    ser.write(b'M')

    # Then write motor values
    for val in vals:
        write_uint16(ser, val, endianness)

    # Write EOT
    ser.write(EOT_CHAR)

def write_uint16(ser: serial.Serial, n: int, endianness: str = 'l'):
    """Write an integer to the serial port as an unsigned 16-bit integer.

    Args:
        n (int): Number to write
        endianness (str): Character representing endian-ness - 'b' for big and
            'l' for little. Default is little.
    """
    _write_bytes(ser, n, endianness, 2)

def read_uint16(ser: serial.Serial, endianness: str = 'l'):
    return _read_bytes(ser, endianness, 2)

def read_uint64(ser: serial.Serial, endianness: str = 'l'):
    return _read_bytes(ser, endianness, 4)

def _read_bytes(ser: serial.Serial, endianness: str, n_bytes: int):
    read_b = ser.read(n_bytes)
    if endianness == 'l':
        ret = int.from_bytes(read_b, 'little')
    else:
        ret = int.from_bytes(read_b, 'big')
    
    return ret

def _write_bytes(ser: serial.Serial, n: int, endianness: str, n_bytes: int):
    if endianness == 'l':
        byte_n = n.to_bytes(n_bytes, 'little')
    else:
        byte_n = n.to_bytes(n_bytes, 'big')
    ser.write(byte_n)
    

def wait_for_connection(ser: serial.Serial, startup_char: bytes, timeout: int):
    """Test for connection with Arduino.

    Blocks until either connection is established with the Arduino or the
    timeout is reached. Returns True when connected; False if timed out.

    Args:
        timeout (int): Time to wait in seconds. Set to 0 or less to never
        timeout.
    """
    start = time.time()
    while ser.read() != startup_char:
        time.sleep(1)
        current = time.time()
        if timeout > 0 and current - start > timeout:
            # timed out, stop attempting to connect
            return False
    ser.write(startup_char)
    # Signal received, connected. Return True.
    return True


if __name__ == '__main__':
    ser = serial.Serial('/dev/ttyUSB0')
    print(ser.name)
    while True:
        write_uint16(ser, 1676)
        write_uint16(ser, 3451)
        # ser.write(b'\x0A')
        print(ser.readline())
        time.sleep(0.5)

