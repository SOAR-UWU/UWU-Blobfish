"""Launch file for testing motors and figuring out motor order."""

from ament_index_python.packages import get_package_share_path
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    pkg_this = get_package_share_path("diagnostics")

    motor_node = Node(
        package="diagnostics",
        executable="motor",
        parameters=[{"config_path": str(pkg_this / "config" / "motor.yaml")}],
    )

    ld = LaunchDescription()
    ld.add_action(motor_node)
    return ld
