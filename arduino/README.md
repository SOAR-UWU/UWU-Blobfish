# Arduino code
This folder contains the code to be uploaded to the Arduino. **Do not place code that should be run on the Jetson here!**

## Interfacing with the Arduino
The `arduino-cli` tool is needed to control upload to the Arduino from the commandline, and will be used to soft reset the Arduino when required. 

## Installing `arduino-cli`
The `arduino-cli` binary file is contained in the `docker` folder in the root of this project, and should be installed automatically when you start the Docker instance. Note that there are **two** versions present in the folder, one for x86 architecture and one for ARM architecture. The ARM one is used by default as the Jetson runs on ARM architecture. **If your system uses x86**, be sure to rename the `arduino-cli_x86` binary to `arduino-cli` so that the right version is installed.

If you are not using the Docker instance, you may alternatively refer to the [installation steps](https://arduino.github.io/arduino-cli/0.35/installation/) to install it. Remember to add the downloaded binary to your [`/bin` path](https://refspecs.linuxfoundation.org/FHS_3.0/fhs/ch03s04.html)!

After installation, install the avr core and code dependencies:

```bash
arduino-cli core install arduino:avr
arduino-cli lib install SimpleSerialProtocol
arduino-cli lib install Servo
```

Compile the code:

```bash
arduino-cli compile --fqbn arduino:avr:nano arduino.ino
```

The header files in this directory may be included with the `--library` option:

```bash
arduino-cli compile --fqbn arduino:avr:nano:cpu=atmega328old --library . main/main.ino
```

And upload it:

```bash
# You may need to replace /dev/ttyUSB0 with the right serial port
arduino-cli upload -p /dev/ttyUSB0 --fqbn arduino:avr:nano:cpu=atmega328old arduino.ino
```

## Arduino-Jetson interface
The functions for interfacing with the Jetson are stored in the `arduino_jetson_interface.h` header file. The `await_connection()` function should be called in `setup()`.