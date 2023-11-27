"""Library with functions to interface with Arduino."""

import time

import serial


def write_uint16(ser: serial.Serial, n: int, endianness: str = 'l'):
    """Write an integer to the serial port as an unsigned 16-bit integer.

    Args:
        n (int): Number to write
        endianness (str): Character representing endian-ness - 'b' for big and
            'l' for little. Default is little.
    """
    if endianness == 'l':
        byte_n = n.to_bytes(2, 'little')
    else:
        byte_n = n.to_bytes(2, 'big')
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

