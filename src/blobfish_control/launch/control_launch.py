import sys
import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    configs = os.path.join(get_package_share_directory('blobfish_control'), 'config', "params.yaml")

    set_manual_setpoints = Node(
        package="blobfish_control",
        executable="manual_setpoint",
        parameters=[configs]
    )

    ld = LaunchDescription()
    ld.add_action(set_manual_setpoints)
    return ld