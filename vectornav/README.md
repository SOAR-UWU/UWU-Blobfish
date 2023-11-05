# Vectornav ROS2 Driver

A ROS2 node for VectorNav INS / GNSS devices. 

This package that provides both raw and sensor_msg interfaces for the VN100, 200, & 300 devices. 
It has been entirely redesigned from the ROS1 package to provide a good basis to build into applications
without requiring modification of the node itself. The majority of the device configuration settings are 
exposed as ROS2 parameters that can be modified from a launch file. 


## QuickStart

Build

1. git clone https://github.com/dawonn/vectornav.git -b ros2
2. cd vectornav 
3. colcon build

Run with ros2 run (Option 1)

(on all terminals) source install/setup.bash

4. (Terminal 1) chmod 666 /dev/tty{tty port name}
5. (Terminal 1) ros2 run vectornav vectornav
6. (Terminal 2) ros2 topic echo /vectornav/raw/common
7. (Terminal 3) ros2 run vectornav vn_sensor_msgs
8. (Terminal 4) ros2 topic echo /vectornav/imu

Run with ros2 launch (Option 2, uses parameters from `vectornav.yaml`)

9. (Terminal 1) ros2 launch vectornav vectornav.launch.py
10. (Terminal 2) ros2 topic echo /vectornav/raw/common
11. (Terminal 3) ros2 topic echo /vectornav/imu

## vectornav node

This node provides a ROS2 interface for a vectornav device. It can be configured
via ROS parameters and publishes sensor data via custom ROS topics as close to raw as possible.


## vn_sensor_msgs node

This node will convert the custom raw data topics into ROS2 sensor_msgs topics to make it easier 
to integrate with other ROS2 packages. 


## References 

[1] [VectorNav](http://www.vectornav.com/)