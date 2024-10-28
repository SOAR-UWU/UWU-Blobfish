"""Main launch file for simulator.

Refer to https://docs.ros.org/en/humble/p/launch/user_docs/source/architecture.html
for list of available launch functions.
"""

from ament_index_python.packages import get_package_share_path
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    pkg_uwu_sim = get_package_share_path("uwu_sim")

    pool_world = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            str(pkg_uwu_sim / "launch" / "pool_world.launch.py")
        )
    )
    gz_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        parameters=[{"config_file": str(pkg_uwu_sim / "config" / "bridge.yaml")}],
    )
    keypress_converter = Node(
        package="blobfish_sim",
        executable="keypress_bridge",
    )

    return LaunchDescription([pool_world, gz_bridge, keypress_converter])
