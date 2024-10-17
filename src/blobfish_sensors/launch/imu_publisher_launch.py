
import os
from sys import executable

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    imu_configs = os.path.join(get_package_share_directory('blobfish_sensors'), 'config', "params.yaml")

    imu_node = Node(
        package="blobfish_sensors",
        executable="imu_publisher",
        parameters=[imu_configs]
    )

    # Create the launch description and populate
    ld = LaunchDescription()
    ld.add_action(imu_node)
    return ld