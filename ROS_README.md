# Main code folder for UWU 2024

The code here is meant for deployment on the **Jetson**. To build and run:

```sh
# Install all dependencies.
rosdep install -i --from-paths .
# Build all packages.
colcon build
# Source ROS2 environment.
source install/local_setup.bash
```

If you don't want to build all the packages, select specific packages using:

```sh
colcon build --packages-up-to <pkgname1> <pkgname2> ...
```

## Arduino Bridge

NOTE: `launch-all.py` does this already.

The Arduino bridge is a node in the `arduino_bridge` package. To start the Arduino bridge node, run:

```sh
# Ensure you already `source install/local_setup.bash`!
ros2 run arduino_bridge bridge
```

The node listens to motor values on the topic `motor_values`. The message format is found in `blobfish_msgs/msg/Motors.msg`.
