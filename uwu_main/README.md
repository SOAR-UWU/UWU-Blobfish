# Main code folder for UWU 2024

The code here is meant for deployment on the **Jetson**. To build and run,

1. Ensure the Docker container is enabled (see `README.md` in root directory)
2. Run the following commands in **this directory**:
```bash
colcon build
source install/local_setup.bash
```
If you don't want / need to build all the packages, use
```bash
colcon build --packages-select <package_name>
```
to build selected packages only.

## Arduino Bridge
The Arduino bridge is a node in the `arduino_publisher` package. To start the Arduino bridge node, run

```bash
ros2 run arduino_publisher arduino_bridge
```

The node listens to motor values on the topic `motor_values`. The message format is found in `motor_msg/msg/Motors.msg`.