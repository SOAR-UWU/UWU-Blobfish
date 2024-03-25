import os
from sys import executable

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    arduino_configs = os.path.join(get_package_share_directory('arduino_bridge'), 'config', "params.yaml")

    motor_bridge = Node(
        package="arduino_bridge",
        executable="bridge",
        parameters=[arduino_configs]
    )

    ld = LaunchDescription()
    ld.add_action(motor_bridge)
    return ld