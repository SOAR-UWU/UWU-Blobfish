# Arduino Bridge

This package contains facilities for publishing messages to the Arduino. For information about the protocol and code used for communication with the Arduino, check the `arduino_bridge/arduino_interface.py` file in this package. General information about the interface follows.

## Usage

Build the package and run it:

```bash
# In the uwu_main directory (which contains the src directory)
colcon build
source install/local_setup.bash
ros2 run arduino_bridge bridge
```

## Arduino Bridge Node

The `bridge` node in this package is run with the `arduino_listener.py` script. This node listens on the `motor_values` topic, and publishes any values it receives from the topic to the Arduino via the Serial interface.

## Arduino interface documentation

The interface depends on two libraries to be run on the Arduino and Jetson respectively. On the Jetson, the interface library is `arduino_interface.py`. On the Arduino, interface library is `arduino_jetson_interface.h`. The interface depends on the [SimpleSerialProtocol](https://www.arduino.cc/reference/en/libraries/simpleserialprotocol/) Arduino library.

### Establish connection

On start, the Arduino first waits to get a connection message from the Jetson. This is in the form of a single character (set to `S` by default) exchanged over the Serial communication. Specifically, the Arduino repeatedly sends `S` over Serial, until it hears `S` back, while the Jetson continuously waits for `S` until it receives it, at which point it sends `S` back once over Serial.

### Motor messages

The motor values are sent as a series of 7 `uint16` values to the Arduino. Each `motor_value` message consists of:

- An initial `M` character
- Seven `uint16` values
- An End-Of-Transmission (EOT) character, `\n`.

If either the `M` or the EOT character are not present, or if the Arduino times out half way while waiting for the message, the message is considered invalid and is discarded.

### Interface tests

The `test/` directory contains code to run tests on the function of the interface. To run these tests, run `colcon test` after building the package. For more specifics about the tests, check the README file in the `test/` directory.
