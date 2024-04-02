import sys
import os

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    base_strategy = Node(
        package="blobfish_control",
        executable="base_strategy"
    )

    sauvc_2024 = Node(
        package="blobfish_control",
        executable="sauvc_2024"
    )

    ld = LaunchDescription()
    ld.add_action(base_strategy)
    ld.add_action(sauvc_2024)
    return ld