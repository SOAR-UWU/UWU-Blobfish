# Arduino code
This folder contains the code to be uploaded to the Arduino. **Do not place code that should be run on the Jetson here!**

## Interfacing with the Arduino
The `arduino-cli` tool is needed to control upload to the Arduino from the commandline, and will be used to soft reset the Arduino when required. Refer to the [installation steps](https://arduino.github.io/arduino-cli/0.35/installation/) to install it.

After installation, install the avr core:

```bash
arduino-cli core install arduino:avr
```

Compile the code:

```bash
arduino-cli compile --fqbn arduino:avr:nano arduino.ino
```

And upload it:

```bash
# You may need to replace /dev/ttyUSB0 with the right serial port
arduino-cli upload -p /dev/ttyUSB0 --fqbn arduino:avr:nano arduino.ino
```

## Arduino-Jetson interface
The functions for interfacing with the Jetson are stored in the `arduino_jetson_interface.h` header file. The `await_connection()` function should be called in `setup()`.