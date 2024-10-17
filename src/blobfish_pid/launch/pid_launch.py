import os
from sys import executable

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    pid_configs = os.path.join(get_package_share_directory('blobfish_pid'), 'config', "params.yaml")

    pid_node = Node(
        package="blobfish_pid",
        executable="pid_node",
        parameters=[pid_configs]
    )

    # Create the launch description and populate
    ld = LaunchDescription()
    ld.add_action(pid_node)
    return ld