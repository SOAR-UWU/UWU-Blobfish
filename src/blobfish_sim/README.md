# Blobfish Sim

Unlike `uwu_sim`, this package contains simulation value mapping nodes and other
Blobfish-specific simulation logic like simulated Arduino bridge, etc.

## Topics Mapped

Referring to [`uwu_sim/config/bridge.yaml`](../uwu_sim/config/bridge.yaml) is a good idea.

### Keypress: `/keypress`@[`blobfish_control/publish_key.py`](../blobfish_control/blobfish_control/publish_key.py)

`blobfish_control/publish_key.py` uses Python's `chr()` & `ord()` for keypresses.
This notably doesn't support arrow keys as a single character. Lowercase, uppercase,
and some key combos (ctrl + key) are supported.

In contrast, Gazebo's keypress publisher uses Qt::Key event codes. See:
- Implementation: https://github.com/gazebosim/gz-gui/blob/gz-gui9/src/plugins/key_publisher/KeyPublisher.cc
- Qt docs for function: https://doc.qt.io/qt-6/qkeyevent.html#key
- Qt key codes: https://doc.qt.io/qt-6/qt.html#Key-enum

Unfortunately, the function used in KeyPublisher.cc doesn't support uppercase &
defaults to uppercase.

I aim to support `chr()` primarily for ease of all other ROS2 nodes. However, that
means arrow keys aren't supported.

Also, I give up, so we only support lowercase alphanumeric keys in simulation now.

Oh this is cursed ROS created its own Python bindings for Qt: https://wiki.ros.org/python_qt_binding

### IMU: `/blobfish/imu_measurements`@[`blobfish_sensors/imu_publisher.py`](../blobfish_sensors/blobfish_sensors/imu_publisher.py)

Instead of emulating `/vectornav/raw/common`, emulating `/blobfish/imu_measurements`
is easier.

### Arduino: `/blobfish/motor_values`@[`arduino_bridge/arduino_listener.py`](../arduino_bridge/arduino_bridge/arduino_listener.py)
